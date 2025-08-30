import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
from src.data_handler import load_data, generate_csv_output
from src.llm import GeminiProvider, OpenAIProvider
from src.compliance_analyzer import LLMCompliancePipeline


def main():
    load_dotenv()
    # Initialize LLM Provider
    # Use GeminiProvider or OpenAIProvider
    # llm_provider = OpenAIProvider(model="gpt-4-mini")
    llm_provider = GeminiProvider(model="gemini-2.5-flash")

    # Initialize Compliance Pipeline
    pipeline = LLMCompliancePipeline(llm_provider=llm_provider)

    try:
        df = load_data('data/sample_data.csv')
    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure the data directory is correctly set up.")
        return

    # Process Dataset
    results = pipeline.process_dataset(df)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"compliance_results_{timestamp}.csv"
    
    # save results to CSV
    generate_csv_output(results, output_file)
    print(f"\n✓ Compliance analysis complete. Results saved to {output_file}")

if __name__ == "__main__":
    main()
