import json
import re
from typing import List
from .data_handler import ComplianceFlag, ComplianceResult, DomainKnowledge, load_regulations_by_directory
from .llm import LLMProvider


class LLMCompliancePipeline:
    def __init__(self, llm_provider: LLMProvider, location: str | None = None):
        """Initialize the pipeline with an LLM provider."""
        self.llm_provider = llm_provider
        self.domain_knowledge = DomainKnowledge()
        ##self.regulations = load_regulations(location=location)
        self.regulations = load_regulations_by_directory()

    def filter_relevant_regulation_dirs(self, feature_name: str, feature_description: str) -> dict:
        """
        Uses the LLM to determine whether a feature is worth checking against each regulation directory.
        Returns a dict of {directory: {"check_regulation": bool, "reasoning": str}}.
        """
        decisions = {}
        for directory, data in self.regulations.items():
            context = data["context"]
            prompt = (
                f"You are a legal analyst helping prioritize which regulations to check for a feature.\n\n"
                f"--- Regulation Context ---\n"
                f"{context}\n\n"
                f"--- Feature to Analyze ---\n"
                f"Name: {feature_name}\n"
                f"Description: {feature_description}\n\n"
                f"QUESTION: Should this feature be checked against the regulation context above?\n"
                f"Only answer YES if the context clearly relates to the feature. If uncertain, say NO.\n\n"
                f"Respond in the following JSON format:\n"
                f"{{\n"
                f"  \"check_regulation\": true|false,\n"
                f"  \"reasoning\": \"Short explanation of why or why not.\"\n"
                f"}}"
            )
            try:
                response = self.llm_provider.generate_json_response(prompt)
                parsed = json.loads(response)
                decisions[directory] = {
                    "check_regulation": bool(parsed.get("check_regulation", False)),
                    "reasoning": parsed.get("reasoning", "No reasoning provided.")
                }
            except Exception as e:
                decisions[directory] = {
                    "check_regulation": False,
                    "reasoning": f"LLM call failed: {str(e)}"
                }
        return decisions

    def create_compliance_prompt(self, feature_name: str, feature_description: str) -> str:
        """
        Creates the prompt for the LLM based on the feature data and loaded regulations.
        """
        
        regulations_text = "\n\n".join([
            f"--- Regulation from file: {file_path} ---\n{content}"
            for file_path, content in self.regulations.items()
        ])

        return (
            f"You are a compliance expert. Analyze the following software feature against the provided regulations.\n"
            f"Identify if geo-specific compliance logic for the feature is REQUIRED, NOT_REQUIRED or UNCERTAIN.\n"
            f"If it's REQUIRED, you MUST state the exact file path from the provided regulations that supports your conclusion.\n\n"
            f"--- Regulations to reference ---\n"
            f"{regulations_text}\n\n"
            f"--- Feature to analyze ---\n"
            f"Feature Name: {feature_name}\n"
            f"Description: {feature_description}\n\n"
            f"Respond with a JSON object containing the following keys:\n"
            f"1. `compliance_flag`: 'REQUIRED', 'NOT_REQUIRED', or 'UNCERTAIN'\n"
            f"2. `confidence_score`: A float from 0.0 to 1.0\n"
            f"3. `reasoning`: A brief explanation for the flag and confidence score.\n"
            f"4. `related_regulations`: An array of relevant regulations (e.g., ['GDPR', 'CCPA']).\n"
            f"5. `geo_regions`: An array of geographic regions affected (e.g., ['EU', 'US']).\n"
            f"6. `source_file`: The full path of the regulation file that directly supports your finding.\n\n"
            f"Example response:\n"
            f"```json\n"
            f"{{ \"compliance_flag\": \"compliant\", \"confidence_score\": 0.9, \"reasoning\": \"The feature uses data anonymization.\", \"related_regulations\": [\"HIPAA\"], \"geo_regions\": [\"US\"], \"source_file\": \"regulations/HIPAA/hipaa_privacy_rule.txt\" }}\n"
            f"```\n"
        )

    def analyze_feature(self, feature_name: str, feature_description: str) -> ComplianceResult:
        """Analyze a single feature for compliance requirements."""
        prompt = self.create_compliance_prompt(
            feature_name, feature_description)
        input()
        try:
            response_obj = self.llm_provider.generate_json_response(prompt)
            result_json = json.loads(response_obj)
            return ComplianceResult(
                feature_name=feature_name,
                compliance_flag=ComplianceFlag(result_json["compliance_flag"]),
                confidence_score=float(result_json["confidence_score"]),
                reasoning=result_json["reasoning"],
                related_regulations=result_json.get("related_regulations", []),
                geo_regions=result_json.get("geo_regions", []),
                source_file=result_json.get("source_file", "N/A")
            )
        except Exception as e:
            print(f"Error analyzing '{feature_name}': {e}")
            return ComplianceResult(
                feature_name=feature_name,
                compliance_flag=ComplianceFlag.UNCERTAIN,
                confidence_score=0.0,
                reasoning=f"Analysis failed: {str(e)}",
                related_regulations=[],
                geo_regions=[],
                source_file="N/A"
            )

    def process_dataset(self, df) -> List[ComplianceResult]:
        """Process the entire dataset."""
        results = []
        print(f"Using LLM: {self.llm_provider.get_model_name()}")
        print("Processing features for compliance analysis...")

        for idx, row in df.iterrows():
            feature_name = row['feature_name']
            feature_description = row['feature_description']
            print(f"[{idx+1}/{len(df)}] Analyzing: {feature_name}")
            regulationfiles = []
            result = self.analyze_feature(feature_name, feature_description)
            results.append(result)
        return results
