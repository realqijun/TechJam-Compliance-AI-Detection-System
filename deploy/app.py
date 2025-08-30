import os
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for

from src.compliance_analyzer import LLMCompliancePipeline
from src.llm import GeminiProvider


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
    # Check if the post request has the file part
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']

    # case for user not selecting a file
    if file.filename == '':
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        try:
            df = pd.read_csv(file)

            # Convert the pandas DataFrame to an HTML table
            csv_html = df.to_html(classes="table-auto w-full")

            # TODO: Integrate compliance analysis logic here and update csv_html accordingly
            # load_dotenv()
            # llm_provider = GeminiProvider(model="gemini-2.5-flash")
            # pipeline = LLMCompliancePipeline(llm_provider=llm_provider)
            # results = pipeline.process_dataset(df)
            # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # output_file = f"compliance_results_{timestamp}.csv"
            # generate_csv_output(results, os.path.join(app.config['UPLOAD_FOLDER'], output_file))
            # csv_html = pd.DataFrame([r.to_dict() for r in results]).to_html(classes="table-auto w-full")

            # Render the output template with the HTML table
            return render_template('output.html', table_data=csv_html)

        except Exception as e:
            return f"Error processing file: {e}"

    return redirect(url_for('index'))

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
