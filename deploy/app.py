import os
import pandas as pd
from flask import render_template, Flask, request, redirect, url_for, send_from_directory, flash
from src.compliance_analyzer import LLMCompliancePipeline
from src.llm import GeminiProvider
from datetime import datetime

# where we save CSV outputs for download
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Check if the file extension is allowed


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Main route for the dashboard and file upload form


@app.route('/')
def index():
    return render_template('index.html')

# Route to handle the file upload


@app.route('/upload', methods=['POST'])
def upload_file():
    # validate
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if not (file and allowed_file(file.filename)):
        return redirect(url_for('index'))

    try:
        # read CSV
        df = pd.read_csv(file)

        # normalize column names expected by pipeline
        df = df.rename(columns={c: c.lower() for c in df.columns})
        if 'feature_name' not in df.columns or 'feature_description' not in df.columns:
            return "Error: CSV must contain 'feature_name' and 'feature_description' columns."

        # read global location from dropdown (empty => None => use all regs)
        raw_loc = request.form.get('location', '').strip()
        global_location = raw_loc or None

        # init provider + pipeline
        # llm_provider = OpenAIProvider(model="gpt-4o-mini")
        llm_provider = GeminiProvider(model="gemini-2.5-flash")
        pipeline = LLMCompliancePipeline(llm_provider=llm_provider, location=global_location)

        # process with ONE location for all rows
        results = pipeline.process_dataset(df)

        # build output df
        out_df = pd.DataFrame([{
            "feature_name": r.feature_name,
            "compliance_flag": r.compliance_flag.value,
            "confidence_score": r.confidence_score,
            "reasoning": r.reasoning,
            "related_regulations": "; ".join(r.related_regulations),
            "geo_regions": "; ".join(r.geo_regions),
        } for r in results])


        # save + render
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_name = f"compliance_results_{ts}.csv"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        out_df.to_csv(out_path, index=True)

        csv_html = out_df.to_html(classes="dataframe table-auto w-full")
        return render_template('output.html', table_data=csv_html)
    except Exception as e:
        return f"Error processing file: {e}"


@app.route('/analyze_one', methods=['POST'])
def analyze_one():
    feature_name = request.form.get('feature_name', '').strip()
    feature_description = request.form.get('feature_description', '').strip()
    location = request.form.get('location', '').strip()

    if not feature_name or not feature_description:
        return redirect(url_for('index') + '?tab=single')

    # Pass the location as a hint (quickest path, no pipeline signature change)
    desc_with_hint = feature_description + (f"\n\n[User-selected region hint: {location}]" if location else "")

    df = pd.DataFrame([{"feature_name": feature_name, "feature_description": desc_with_hint}])

    # pick provider
    # llm_provider = OpenAIProvider(model="gpt-4o-mini")
    llm_provider = GeminiProvider(model="gemini-2.5-flash")

    pipeline = LLMCompliancePipeline(llm_provider=llm_provider, location=location)
    results = pipeline.process_dataset(df)

    # build result table for output.html
    table_df = pd.DataFrame([{
        "feature_name": r.feature_name,
        "compliance_flag": r.compliance_flag.value,
        "confidence_score": r.confidence_score,
        "reasoning": r.reasoning,
        "related_regulations": "; ".join(r.related_regulations),
        "geo_regions": "; ".join(r.geo_regions),
    } for r in results])

    csv_html = table_df.to_html(classes="dataframe table-auto w-full")
    return render_template('output.html', table_data=csv_html)


if __name__ == '__main__':
    app.run()
