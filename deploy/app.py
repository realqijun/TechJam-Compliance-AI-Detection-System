from src.data_handler import ComplianceFlag, ComplianceResult
from src.llm import GeminiProvider
from src.compliance_analyzer import LLMCompliancePipeline
import os
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for
from dotenv import load_dotenv
from datetime import datetime

# Add the project's root directory to the system path for imports
import sys
from os.path import dirname, join, abspath

# Add the project root to the system path
sys.path.insert(0, abspath(join(dirname(__file__), '..')))


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
            load_dotenv()
            llm_provider = GeminiProvider(model="gemini-2.5-flash")
            pipeline = LLMCompliancePipeline(llm_provider=llm_provider)
            results = pipeline.process_dataset(df)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"compliance_results_{timestamp}.csv"
            generate_csv_output(results, os.path.join(
                app.config['UPLOAD_FOLDER'], output_file))
            csv_html = pd.DataFrame([r.to_dict() for r in results]).to_html(
                classes="table-auto w-full")

            # Render the output template with the HTML table
            return render_template('output.html', table_data=csv_html)

        except Exception as e:
            return f"Error processing file: {e}"

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
