import json
import re
from typing import List
from .data_handler import ComplianceFlag, ComplianceResult, DomainKnowledge, load_regulations, load_regulations_by_directory
from .llm import LLMProvider
import time

class LLMCompliancePipeline:
    def __init__(self, llm_provider: LLMProvider, location: str | None = None):
        """Initialize the pipeline with an LLM provider."""
        self.llm_provider = llm_provider
        self.domain_knowledge = DomainKnowledge()
        self.regulations_by_directory = None
        self.regulations = load_regulations(location=location)
        self.location = location
        if location is None:
            self.regulations_by_directory = load_regulations_by_directory()
            
    def filter_and_flatten_files(self, decisions: dict[str, dict[str, any]], regulations: dict[str, dict[str, any]]) -> list[str]:
        """
        Filters out regulation directories that are not relevant and returns a flat list of file paths
        from the remaining directories.

        Args:
            decisions: Output of filter_relevant_regulation_dirs
            regulations: A copy of the full regulations dictionary

        Returns:
            A flat list of file paths from directories marked as relevant.
        """
        filtered_files = []
        for directory, decision in decisions.items():
            if decision.get("check_regulation", False):
                reg_entry = regulations.get(directory, {})
                files = reg_entry.get("files", [])
                filtered_files.extend(files)
        return filtered_files

##    def filter_relevant_regulation_dirs(self, feature_name: str, feature_description: str) -> dict:
##        """
##        Uses the LLM to determine whether a feature is worth checking against each regulation directory.
##        Returns a dict of {directory: {"check_regulation": bool, "reasoning": str}}.
##        """
##        decisions = {}
##        for directory, data in self.regulations_by_directory.items():
##            context = data["context"]
##            prompt = (
##                f"You are a legal analyst helping prioritize which regulations to check for a feature.\n\n"
##                f"--- Regulation Context ---\n"
##                f"{context}\n\n"
##                f"--- Feature to Analyze ---\n"
##                f"Name: {feature_name}\n"
##                f"Description: {feature_description}\n\n"
##                f"QUESTION: Should this feature be checked against the regulation context above?\n"
##                f"Only answer YES if the context clearly relates to the feature. If uncertain, say NO.\n\n"
##                f"Respond in the following JSON format:\n"
##                f"{{\n"
##                f"  \"check_regulation\": true|false,\n"
##                f"  \"reasoning\": \"Short explanation of why or why not.\"\n"
##                f"}}"
##            )
##            try:
##                response = self.llm_provider.generate_json_response(prompt)
##                parsed = json.loads(response)
##                decisions[directory] = {
##                    "check_regulation": bool(parsed.get("check_regulation", False)),
##                    "reasoning": parsed.get("reasoning", "No reasoning provided.")
##                }
##            except Exception as e:
##                decisions[directory] = {
##                    "check_regulation": False,
##                    "reasoning": f"LLM call failed: {str(e)}"
##                }
##        return decisions
    def filter_relevant_regulation_dirs(self, feature_name: str, feature_description: str) -> dict:
        """
        Uses the LLM once to determine whether a feature is worth checking against each regulation directory.
        Returns a dict of {directory: {"check_regulation": bool, "reasoning": str}}.
        """
        # Build the combined regulation contexts section
        regulation_sections = []
        for directory, data in self.regulations_by_directory.items():
            context = data.get("context", "")
            regulation_sections.append(f"Directory: {directory}\nContext: {context}")
        
        all_contexts = "\n\n".join(regulation_sections)

        # Build the full prompt
        prompt = (
            f"You are a legal analyst helping prioritize which regulation directories to check for a software feature.\n\n"
            f"--- All Regulation Contexts ---\n"
            f"{all_contexts}\n\n"
            f"--- Feature to Analyze ---\n"
            f"Name: {feature_name}\n"
            f"Description: {feature_description}\n\n"
            f"QUESTION:\n"
            f"For each directory above, decide whether this feature should be checked against the regulation context.\n"
            f"Only say TRUE if the context clearly applies to the feature. If not clear, say FALSE.\n\n"
            f"Respond in this exact JSON format:\n"
            f"{{\n"
            f"  \"<directory_path>\": {{\n"
            f"     \"check_regulation\": true|false,\n"
            f"     \"reasoning\": \"Short explanation of why or why not.\"\n"
            f"  }},\n"
            f"  ...\n"
            f"}}"
        )

        # Call LLM once
        try:
            response = self.llm_provider.generate_json_response(prompt)
            parsed = json.loads(response)
            return parsed
        except Exception as e:
            print(f"[ERROR] LLM failed during regulation filtering: {e}")
            # Return all as unchecked if something fails
            return {
                directory: {
                    "check_regulation": False,
                    "reasoning": f"LLM call failed: {str(e)}"
                }
                for directory in self.regulations_by_directory
            }
    
    def create_compliance_prompt(self, feature_name: str, feature_description: str) -> str:
        """
        Creates the prompt for the LLM based on the feature data and loaded regulations.
        """
        files_to_include = None
        if self.location is None:
            decisions = self.filter_relevant_regulation_dirs(feature_name, feature_description)
            filenames_to_include = self.filter_and_flatten_files(decisions, self.regulations_by_directory)
            files_to_include = {file_path: content for file_path, content in self.regulations.items() if file_path in filenames_to_include}
        else:
            files_to_include = self.regulations
            
        regulations_text = "\n\n".join([
            f"--- Regulation from file: {file_path} ---\n{content}"
            for file_path, content in files_to_include.items()
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
            ttime = time.time()
            result = self.analyze_feature(feature_name, feature_description)
            print(time.time()-ttime)
            results.append(result)
        return results
