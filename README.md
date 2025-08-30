# GeoRegulator

## About
GeoRegulator is a **Compliance Checker** powered by **AI**. Focusing on development features with support for preset terminologies. This project relies heavily on social media regulations from across the world. 
This project is a submission for TikTok's TechJam 2025 Hackathon.

## Problem Statement
The goal of this project is to build a prototype system that uses LLM capabilities to flag features that require geo-specific compliance logic. Our solution transforms regulatory detection from a blind spot into a traceable, auditable output. By doing so, we aim to empower teams at companies like TikTok to proactively implement legal safeguards before a feature launches, generate auditable evidence of regulatory screening, and confidently respond to regulatory inquiries.

--- 

## Core Functionality
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

## How to run
1. Create a API Key either from [Google AI Studio](https://aistudio.google.com/) or [OpenAI](https://platform.openai.com/docs/api-reference/project-api-keys).
2. Clone the project onto your machine.
3. Create a `.env` file in the root directory of the project and insert your API Key.
4. Create and source your own Python Virtual Environment or use your system's global environment instead.
5. Run `pip install -r requirement.txt`.
6. Edit the code in main.py to use your preference of AI models, then insert your feature list(in csv format) into the data/ folder.
7. Run `python main.py`.
8. View the results in compliance_results_yyyymmdd_hhmmss.csv.

---

## Specifications
 - Python 3.9 or above

---

## References
1. EU Digital Service Act. [DSA](https://en.wikipedia.org/wiki/Digital_Services_Act)
2. California state law - [Protecting Our Kids from Social Media Addiction Act](https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=202320240SB976)
3. Florida state law - [Online Protections for Minors](https://www.flsenate.gov/Session/Bill/2024/3)
4. Utah state law - [Utah Social Media Regulation Act](https://en.wikipedia.org/wiki/Utah_Social_Media_Regulation_Act)
5. US law on reporting child sexual abuse content to NCMEC -  [Reporting requirements of providers](https://www.law.cornell.edu/uscode/text/18/2258A)