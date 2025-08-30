# GeoRegulator
**An AI-powered Compliance Checker for Software Features**
This project is a submission for TikTok's TechJam 2025 Hackathon.

## Problem Statement ❔
The goal of this project is to build a prototype system that uses LLM capabilities to flag features that require geo-specific compliance logic. Our solution transforms regulatory detection from a blind spot into a traceable, auditable output, empowering teams to proactively implement legal safeguards and confidently respond to regulatory inquiries.

## Core Functionality 💪
GeoRegulator is a sophisticated Compliance Checker powered by a large language model. It's designed to analyze software feature artifacts—such as titles and descriptions—and automatically determine if they require geo-specific compliance.
The system's key features include:
 - Automated Compliance Analysis: Our core LLM pipeline analyzes feature descriptions against a provided knowledge base of regulations to flag potential compliance requirements.
 - Traceable, Auditable Output: For every analysis, the system provides not only a compliance flag but also clear reasoning and, most importantly, the exact source file from which the regulation was derived. This creates a clear, auditable trail.
 - Cost Reduction: By automating the initial screening process, GeoRegulator significantly reduces the manual effort and time required to identify and manage geo-compliance needs.
 - Mitigated Regulatory Exposure: The system minimizes legal and financial risks by helping teams identify and address compliance gaps before a feature is launched. 
 - Transparency: The auditable evidence trail streamlines communication and provides clear documentation for regulatory inquiries and audits.

---

## The team:
1. Leader: [Chew Jia Hui, Bryan](https://github.com/bryanjhc)
2. [Chew En Rui, Samuel](https://github.com/Monochromas)
3. [Leonardo Wolf](https://github.com/leowolf275)
4. [Yashvan Alagirisamy](https://github.com/YashvanGH)
5. [Ang Qi Jun](https://github.com/realqijun)

---

## Getting Started 🚀

### Prerequisites
 - Python 3.9 or above
 - An API Key from either [Google AI Studio](https://aistudio.google.com/) or [OpenAI](https://platform.openai.com/docs/api-reference/project-api-keys).

### Installation

1. Clone the project onto your machine: <br> `git clone https://github.com/bryanjhc/georegulator.git`
2. Navigate to the project directory: <br> `cd georegulator`
3. Create and activate a Python virtual environment.
4. Install the required libraries: <br> `pip install -r requirements.txt`
5. Create a `.env` file in the root directory and add your API key: <br> `GOOGLE_API_KEY="your_api_key_here"` <br> or <br> `OPENAI_API_KEY="your_api_key_here"`

### How to Run
1. Insert your feature list (in CSV format with `feature_name` and `feature_description` columns) into the `data/` folder.
2. Run the application: <br> `python main.py`
The results will be generated in a CSV file in the `uploads/` folder with a timestamped filename (e.g., `compliance_results_yyyymmdd_hhmmss.csv`).

---

## References
1. EU Digital Service Act. [DSA](https://en.wikipedia.org/wiki/Digital_Services_Act)
2. California state law - [Protecting Our Kids from Social Media Addiction Act](https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=202320240SB976)
3. Florida state law - [Online Protections for Minors](https://www.flsenate.gov/Session/Bill/2024/3)
4. Utah state law - [Utah Social Media Regulation Act](https://en.wikipedia.org/wiki/Utah_Social_Media_Regulation_Act)
5. US law on reporting child sexual abuse content to NCMEC -  [Reporting requirements of providers](https://www.law.cornell.edu/uscode/text/18/2258A)