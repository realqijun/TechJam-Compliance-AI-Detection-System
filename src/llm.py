from parse import load_data
import pandas as pd
import os
import json
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from openai import OpenAI
from datetime import datetime
import csv
from dotenv import load_dotenv

class ComplianceFlag(Enum):
    REQUIRED = "REQUIRED"
    NOT_REQUIRED = "NOT_REQUIRED"
    UNCERTAIN = "UNCERTAIN"

@dataclass
class ComplianceResult:
    feature_name: str
    compliance_flag: ComplianceFlag
    confidence_score: float
    reasoning: str
    related_regulations: List[str]
    geo_regions: List[str]

# Translates the common terminology to the full version
class DomainKnowledge:
    """Maps TikTok internal terminology to clear descriptions"""
    def __init__(self, terminology_csv_path: str = 'data/terminology_table.csv'):
        # Load terminology from CSV file
        self.terminology = self.load_terminology_from_csv(terminology_csv_path)

        self.regulations = {
            "EU DSA": {
                "keywords": ["EU", "DSA", "Digital Services Act", "transparency", "content moderation", "Article 16"],
                "indicators": ["visibility lock", "flagged content", "removal mechanisms", "transparency"]
            },
            "California SB976": {
                "keywords": ["California", "SB976", "teens", "personalization", "PF default"],
                "indicators": ["disable PF", "under 18", "California", "personalization requirements"]
            },
            "Florida Online Protections for Minors": {
                "keywords": ["Florida", "minors", "parental", "notifications"],
                "indicators": ["parental control", "minor accounts", "parental notifications"]
            },
            "Utah Social Media Regulation Act": {
                "keywords": ["Utah", "curfew", "minors", "login restriction"],
                "indicators": ["curfew", "night hours", "Utah boundaries", "login restriction"]
            },
            "US NCMEC": {
                "keywords": ["NCMEC", "child abuse", "federal law", "CSAM"],
                "indicators": ["child sexual abuse", "NCMEC", "T5", "abuse content scanner"]
            }
        }

    def load_terminology_from_csv(self, csv_path: str) -> Dict[str, str]:
        """Load terminology from CSV file"""
        terminology = {}
        try:
            df = load_data(csv_path)
            # Assuming CSV has columns 'term' and 'explanation' or first two columns
            for _, row in df.iterrows():
                term = str(row.iloc[0]).strip()  # First column is term
                # Second column is explanation
                explanation = str(row.iloc[1]).strip()
                terminology[term] = explanation
            print(f"Loaded {len(terminology)} terms from {csv_path}")
            return terminology
        except Exception as e:
            print(f"Warning: Could not load terminology from {csv_path}: {e}")
            # Fallback to hardcoded terminology
            return {
                "NR": "Not recommended",
                "PF": "Personalized feed",
                "GH": "Geo-handler; a module responsible for routing features based on user region",
                "CDS": "Compliance Detection System",
                "DRT": "Data retention threshold; duration for which logs can be stored",
                "LCP": "Local compliance policy",
                "Redline": "Flag for legal review",
                "Softblock": "A user-level limitation applied silently without notifications",
                "Spanner": "A synthetic name for a rule engine",
                "ShadowMode": "Deploy feature in non-user-impact way to collect analytics only",
                "T5": "Tier 5 sensitivity data",
                "ASL": "Age-sensitive logic",
                "Glow": "A compliance-flagging status",
                "NSP": "Non-shareable policy",
                "Jellybean": "Feature name for internal parental control system",
                "EchoTrace": "Log tracing mode to verify compliance routing",
                "BB": "Baseline Behavior",
                "Snowcap": "A synthetic codename for the child safety policy framework",
                "FR": "Feature rollout status",
                "IMT": "Internal monitoring trigger"
            }

    def translate_description(self, description: str) -> str:
        """Replace internal jargon with clear descriptions"""
        translated = description
        for term, definition in self.terminology.items():
            # Replace standalone terms (word boundaries)
            pattern = r'\b' + re.escape(term) + r'\b'
            replacement = f"{term} ({definition})"
            translated = re.sub(pattern, replacement, translated, flags=re.IGNORECASE)
        return translated

# Main LLM Pipeline
class LLMCompliancePipeline:
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        """
        Initialize the LLM pipeline

        Args:
            api_key: OpenAI API key (if None, will try to use environment variable)
            model: OpenAI model to use
        """
        self.model = model
        self.domain_knowledge = DomainKnowledge()

    def create_compliance_prompt(self, feature_name: str, feature_description: str) -> str:
        """Create the LLM prompt for compliance detection"""

        translated_description = self.domain_knowledge.translate_description(
            feature_description)

        prompt = f"""
        You are a compliance expert analyzing TikTok features for geo-specific legal requirements.
        FEATURE TO ANALYZE:
        Name: {feature_name}
        Description: {translated_description}

        REGULATIONS TO CONSIDER:
        1. EU Digital Services Act (DSA) - Content moderation, transparency, removal mechanisms
        2. California SB976 - Teen social media protections, personalized feed restrictions
        3. Florida Online Protections for Minors - Parental controls, minor notifications
        4. Utah Social Media Regulation Act - Curfew restrictions, age gates for minors
        5. US NCMEC Reporting - Child sexual abuse material detection and reporting

        ANALYSIS CRITERIA:
        ✅ REQUIRED: Feature explicitly implements region-specific legal compliance (e.g., "Utah minors", "California teens", "EU DSA")
        ❌ NOT REQUIRED: Feature is business-driven, global testing, or general safety without legal mandate
        ❓ UNCERTAIN: Unclear intention, ambiguous regional restrictions, or missing context

        Your task:
        1. Determine if this feature requires geo-specific compliance logic
        2. Provide clear reasoning
        3. List relevant regulations (if any)
        4. Identify target geographic regions
        5. Assign confidence score (0.0-1.0)

        Respond in this exact JSON format:
        {{
            "compliance_flag": "REQUIRED|NOT_REQUIRED|UNCERTAIN",
            "confidence_score": 0.0-1.0,
            "reasoning": "Clear explanation of your decision",
            "related_regulations": ["regulation1", "regulation2"],
            "geo_regions": ["region1", "region2"]
        }}

        Focus on explicit legal compliance indicators, not general business or safety features.
        """

        return prompt

    def analyze_feature(self, feature_name: str, feature_description: str) -> ComplianceResult:
        """Analyze a single feature for compliance requirements"""

        prompt = self.create_compliance_prompt(feature_name, feature_description)

        try:
            response = client.chat.completions.create(model=self.model,
            messages=[
                {"role": "system", "content": "You are a legal compliance expert specializing in tech platform regulations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temperature for consistent results
            max_tokens=500)

            # Parse the JSON response
            result_text = response.choices[0].message.content.strip()

            # Extract JSON from response (in case there's extra text)
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result_json = json.loads(json_match.group())
            else:
                # Fallback parsing
                result_json = json.loads(result_text)

            return ComplianceResult(
                feature_name=feature_name,
                compliance_flag=ComplianceFlag(result_json["compliance_flag"]),
                confidence_score=result_json["confidence_score"],
                reasoning=result_json["reasoning"],
                related_regulations=result_json.get("related_regulations", []),
                geo_regions=result_json.get("geo_regions", [])
            )

        except Exception as e:
            print(f"Error analyzing {feature_name}: {e}")
            # Return uncertain result as fallback
            return ComplianceResult(
                feature_name=feature_name,
                compliance_flag=ComplianceFlag.UNCERTAIN,
                confidence_score=0.0,
                reasoning=f"Error during analysis: {str(e)}",
                related_regulations=[],
                geo_regions=[]
            )

    def process_dataset(self, df: pd.DataFrame) -> List[ComplianceResult]:
        """Process entire dataset"""
        results = []

        print("Processing features for compliance analysis...")
        for idx, row in df.iterrows():
            feature_name = row['feature_name']
            feature_description = row['feature_description']

            print(f"Analyzing {idx+1}/{len(df)}: {feature_name}")
            result = self.analyze_feature(feature_name, feature_description)
            results.append(result)

        return results

    def generate_csv_output(self, results: List[ComplianceResult], output_path: str):
        """Generate CSV output for submission"""

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'feature_name',
                'compliance_flag',
                'confidence_score',
                'reasoning',
                'related_regulations',
                'geo_regions'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for result in results:
                writer.writerow({
                    'feature_name': result.feature_name,
                    'compliance_flag': result.compliance_flag.value,
                    'confidence_score': result.confidence_score,
                    'reasoning': result.reasoning,
                    'related_regulations': '; '.join(result.related_regulations),
                    'geo_regions': '; '.join(result.geo_regions)
                })

        print(f"Results saved to {output_path}")


if __name__ == "__main__":
    load_dotenv()
    client = OpenAI()
    pipeline = LLMCompliancePipeline(model="gpt-3.5-turbo")
    df = load_data('data/sample_data.csv')

    # process dataset and write the results to CSV
    results = pipeline.process_dataset(df)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"compliance_results_{timestamp}.csv"
    pipeline.generate_csv_output(results, output_file)
