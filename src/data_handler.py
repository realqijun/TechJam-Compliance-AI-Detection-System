import pandas as pd
import re
import os
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum
import csv
import fnmatch

def load_data(file_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} features from {file_path}")
        return df
    except Exception as e:
        print(f"Error loading data: {e}, returning empty DataFrame instead.")
        return pd.DataFrame()


class ComplianceFlag(Enum):
    REQUIRED = "REQUIRED"
    NOT_REQUIRED = "NOT_REQUIRED"
    UNCERTAIN = "UNCERTAIN"


@dataclass
class ComplianceResult:
    """Result of compliance analysis for a feature"""
    feature_name: str
    compliance_flag: ComplianceFlag
    confidence_score: float
    reasoning: str
    related_regulations: list[str]
    geo_regions: list[str]
    source_file: str  # Added from previous conversation

    def to_dict(self) -> dict:
        """Convert to dictionary for CSV export"""
        return {
            'feature_name': self.feature_name,
            'compliance_flag': self.compliance_flag.value,
            'confidence_score': self.confidence_score,
            'reasoning': self.reasoning,
            'related_regulations': '; '.join(self.related_regulations),
            'geo_regions': '; '.join(self.geo_regions),
            'source_file': self.source_file
        }


class DomainKnowledge:
    """Maps internal terminology to clear descriptions and provides regulation data."""
    DEFAULT_TERMINOLOGY = {
        "NR": "Not recommended",
        "PF": "Personalized feed",
        "GH": "Geo-handler; a module for routing features based on user region",
        "CDS": "Compliance Detection System",
        "DRT": "Data retention threshold",
        "LCP": "Local compliance policy",
        "Redline": "Flag for legal review",
        "Softblock": "A user-level limitation applied silently",
        "Spanner": "A synthetic name for a rule engine",
        "ShadowMode": "Deploy feature in non-user-impact way to collect analytics",
        "T5": "Tier 5 sensitivity data",
        "ASL": "Age-sensitive logic",
        "Glow": "A compliance-flagging status",
        "NSP": "Non-shareable policy",
        "Jellybean": "Internal parental control system",
        "EchoTrace": "Log tracing mode to verify compliance routing",
        "BB": "Baseline Behavior",
        "Snowcap": "Codename for the child safety policy framework",
        "FR": "Feature rollout status",
        "IMT": "Internal monitoring trigger"
    }

    REGULATIONS = {
        "EU Digital Services Act (DSA)": {
            "keywords": ["EU", "DSA", "Digital Services Act", "transparency", "content moderation", "Article 16"],
            "indicators": ["visibility lock", "flagged content", "removal mechanisms"]
        },
        "California SB976": {
            "keywords": ["California", "SB976", "teens", "personalization", "PF default"],
            "indicators": ["disable PF", "under 18", "California"]
        },
        "Florida Online Protections for Minors": {
            "keywords": ["Florida", "minors", "parental", "notifications"],
            "indicators": ["parental control", "minor accounts", "parental notifications"]
        },
        "Utah Social Media Regulation Act": {
            "keywords": ["Utah", "curfew", "minors", "login restriction"],
            "indicators": ["curfew", "night hours", "Utah boundaries"]
        },
        "US NCMEC Reporting": {
            "keywords": ["NCMEC", "child abuse", "federal law", "CSAM"],
            "indicators": ["child sexual abuse", "NCMEC", "T5", "abuse content scanner"]
        }
    }

    def __init__(self, terminology_csv_path: str = 'data/terminology_table.csv'):
        self.terminology = self._load_terminology(terminology_csv_path)

    def _load_terminology(self, csv_path: str) -> Dict[str, str]:
        """Load terminology from CSV, falling back to defaults."""
        try:
            df = pd.read_csv(csv_path, header=None)
            return {str(row[0]).strip(): str(row[1]).strip() for _, row in df.iterrows()}
        except Exception:
            return self.DEFAULT_TERMINOLOGY

    def translate_description(self, description: str) -> str:
        """Replace internal jargon with clear descriptions."""
        translated = description
        for term, definition in self.terminology.items():
            pattern = r'\b' + re.escape(term) + r'\b'
            translated = re.sub(
                pattern, f"{term} ({definition})", translated, flags=re.IGNORECASE)
        return translated


def generate_csv_output(results: list[ComplianceResult], output_path: str):
    """Generate CSV output for submission."""
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = results[0].to_dict().keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([r.to_dict() for r in results])


def load_regulations(base_path: Optional[str] = 'regulations', location: Optional[str] = None) -> Dict[str, str]:
    """
    Recursively loads all .txt files from the regulations directory.
    If `location` is provided, only loads files inside subfolders whose name matches (case-insensitive).
    Returns a dictionary mapping the file path to its content.
    """
    regulations_data = {}
    if not os.path.exists(base_path):
        print(f"Warning: Regulations directory not found at '{base_path}'.")
        return regulations_data

    for dirpath, _, filenames in os.walk(base_path):
        folder_name = os.path.basename(dirpath)

        # Apply filter only if location is specified
        if location and location not in folder_name:
            continue

        for filename in filenames:
            if filename.endswith('.txt'):
                file_path = os.path.join(dirpath, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        regulations_data[file_path] = content
                except Exception as e:
                    print(f"Error reading file '{file_path}': {e}")

    return regulations_data


def load_regulations_by_directory(base_path: str = 'regulations') -> Dict[str, str]:
    """
    Recursively loads all .txt files from the regulations directory.
    Returns a dictionary mapping the file path to its content.
    regulations_data = {directory: {context: <context>, files: []}}
    """
    regulations_data = {}
    if not os.path.exists(base_path):
        print(f"Warning: Regulations directory not found at '{base_path}'.")
        return regulations_data


    if not os.path.exists(base_path):
        print(f"Warning: Regulations directory not found at '{base_path}'.")
        return regulations_data

    # Only go one level deep (immediate subdirectories)
    for entry in os.listdir(base_path):
        subdir_path = os.path.join(base_path, entry)
        if os.path.isdir(subdir_path):
            context_path = os.path.join(subdir_path, 'context.txt')
            format_path = os.path.join(subdir_path, 'format.txt')

            # Read context
            try:
                with open(context_path, 'r', encoding='utf-8') as f:
                    context = f.read().strip()
            except Exception as e:
                print(f"Warning: Could not read context.txt in {entry}: {e}")
                context = ""

            # Read pattern
            try:
                with open(format_path, 'r', encoding='utf-8') as f:
                    pattern = f.read().strip()
            except Exception as e:
                print(f"Warning: Could not read format.txt in {entry}: {e}")
                pattern = "*.txt"  # fallback to catch-all

            # Match files
            matched_files = []
            for file in os.listdir(subdir_path):
                if fnmatch.fnmatch(file, pattern) and file not in ('context.txt', 'format.txt'):
                    matched_files.append(file)

            regulations_data[entry] = {
                "context": context,
                "files": matched_files
            }
    return regulations_data

##regzz = load_regulations_by_directory('..\\regulations')


if __name__ == "__main__":
    # run this as a script to test data loading
    df = load_data('data/sample_data.csv')
    if df.empty:
        print("No data loaded. Please check your file path.")

