import json
import re
from typing import List
from data_handler import ComplianceFlag, ComplianceResult, DomainKnowledge
from llm import LLMProvider


class LLMCompliancePipeline:
    def __init__(self, llm_provider: LLMProvider):
        """Initialize the pipeline with an LLM provider."""
        self.llm_provider = llm_provider
        self.domain_knowledge = DomainKnowledge()

    def create_compliance_prompt(self, feature_name: str, feature_description: str) -> str:
        """Create the LLM prompt for compliance detection."""
        translated_description = self.domain_knowledge.translate_description(
            feature_description)
        regulations_str = '\n'.join([
            f"- {name}" for name in self.domain_knowledge.REGULATIONS.keys()
        ])

        prompt = f"""
        You are a compliance expert analyzing features for geo-specific legal requirements.
        
        FEATURE TO ANALYZE:
        Name: {feature_name}
        Description: {translated_description}

        REGULATIONS TO CONSIDER:
        {regulations_str}

        ANALYSIS CRITERIA:
        - REQUIRED: Feature explicitly implements region-specific legal compliance (e.g., "Utah minors", "California teens", "EU DSA").
        - NOT_REQUIRED: Feature is business-driven, global testing, or general safety without legal mandate.
        - UNCERTAIN: Unclear intention, ambiguous regional restrictions, or missing context.

        Your task:
        1. Determine if this feature requires geo-specific compliance logic.
        2. Provide clear reasoning based on the provided text.
        3. List relevant regulations (if any) and target geographic regions.
        4. Assign a confidence score (0.0-1.0) for your analysis.

        Respond in this exact JSON format. Do not include any other text.
        {{
            "compliance_flag": "REQUIRED|NOT_REQUIRED|UNCERTAIN",
            "confidence_score": 0.0-1.0,
            "reasoning": "Clear explanation of your decision",
            "related_regulations": ["regulation1", "regulation2"],
            "geo_regions": ["region1", "region2"]
        }}
        """
        return prompt.strip()

    def analyze_feature(self, feature_name: str, feature_description: str) -> ComplianceResult:
        """Analyze a single feature for compliance requirements."""
        prompt = self.create_compliance_prompt(
            feature_name, feature_description)
        try:
            result_json_str = self.llm_provider.generate_json_response(prompt)
            
            # Clean and parse JSON response
            result_json = json.loads(result_json_str)

            return ComplianceResult(
                feature_name=feature_name,
                compliance_flag=ComplianceFlag(result_json["compliance_flag"]),
                confidence_score=float(result_json["confidence_score"]),
                reasoning=result_json["reasoning"],
                related_regulations=result_json.get("related_regulations", []),
                geo_regions=result_json.get("geo_regions", [])
            )
        except Exception as e:
            print(f"Error analyzing '{feature_name}': {e}")
            return ComplianceResult(
                feature_name=feature_name,
                compliance_flag=ComplianceFlag.UNCERTAIN,
                confidence_score=0.0,
                reasoning=f"Analysis failed: {str(e)}",
                related_regulations=[],
                geo_regions=[]
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
            result = self.analyze_feature(feature_name, feature_description)
            results.append(result)
        return results
