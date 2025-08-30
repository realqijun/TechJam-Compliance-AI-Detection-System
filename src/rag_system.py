import chromadb
import os
import uuid

client = chromadb.PersistentClient(path="./chroma_db")

# Each collection assigned to each regulation
CS_CS_HB_3_collection = client.get_or_create_collection(name="CS_CS_HB_3")
EU_DSA_Regulations_collection = client.get_or_create_collection(name="EU_DSA_Regulations")
SB976_POKSMAA_collection = client.get_or_create_collection(name="SB976_POKSMAA")
UTAH_SocialMediaRegulation_collection = client.get_or_create_collection(name="UTAH_SocialMediaRegulation")
US_reporting_child_sexual_abuse_collection = client.get_or_create_collection(name="US_reporting_child_sexual_abuse")

# open all txt files in CS_CS_HB_3 directory and put them into a list[str]
# CS_CS_HB_3_policies = []
# for filename in os.listdir("../regulations/CS_CS_HB_3"):
#     if filename.endswith(".txt"):
#         with open(os.path.join("../regulations/CS_CS_HB_3", filename), "r", encoding="utf-8") as file:
#             content = file.read()
#             CS_CS_HB_3_policies.append(f"{filename}\n{content}")
# CS_CS_HB_3_policies: list[str] = CS_CS_HB_3_policies
# CS_CS_HB_3_collection.add(
#     ids=[str(uuid.uuid4()) for _ in CS_CS_HB_3_policies],
#     documents=CS_CS_HB_3_policies,
#     metadatas=[{"source": filename} for filename in os.listdir("../regulations/CS_CS_HB_3") if filename.endswith(".txt")]
# )

# EU DSA Regulations
# EU_DSA_Regulations_policies = []
# for filename in os.listdir("../regulations/EU Digital Service Act"):
#     if filename.endswith(".txt"):
#         with open(os.path.join("../regulations/EU Digital Service Act", filename), "r", encoding="utf-8") as file:
#             content = file.read()
#             EU_DSA_Regulations_policies.append(f"{filename}\n{content}")
# EU_DSA_Regulations_policies: list[str] = EU_DSA_Regulations_policies
# EU_DSA_Regulations_collection.add(
#     ids=[str(uuid.uuid4()) for _ in EU_DSA_Regulations_policies],
#     documents=EU_DSA_Regulations_policies,
#     metadatas=[{"source": filename} for filename in os.listdir("../regulations/EU Digital Service Act") if filename.endswith(".txt")]
# )

# SB976 POKSMAA
# SB976_POKSMAA_policies = []
# for filename in os.listdir("../regulations/SB976_POKSMAA"):
#     if filename.endswith(".txt"):
#         with open(os.path.join("../regulations/SB976_POKSMAA", filename), "r", encoding="utf-8") as file:
#             content = file.read()
#             SB976_POKSMAA_policies.append(f"{filename}\n{content}")
# SB976_POKSMAA_policies: list[str] = SB976_POKSMAA_policies
# SB976_POKSMAA_collection.add(
#     ids=[str(uuid.uuid4()) for _ in SB976_POKSMAA_policies],
#     documents=SB976_POKSMAA_policies,
#     metadatas=[{"source": filename} for filename in os.listdir("../regulations/SB976_POKSMAA") if filename.endswith(".txt")]
# )

# UTAH Social Media Regulation
# UTAH_SocialMediaRegulation_policies = []
# for filename in os.listdir("../regulations/UTAH_SocialMediaRegulation"):
#     if filename.endswith(".txt"):
#         with open(os.path.join("../regulations/UTAH_SocialMediaRegulation", filename), "r", encoding="utf-8") as file:
#             content = file.read()
#             UTAH_SocialMediaRegulation_policies.append(f"{filename}\n{content}")
# UTAH_SocialMediaRegulation_policies: list[str] = UTAH_SocialMediaRegulation_policies
# UTAH_SocialMediaRegulation_collection.add(
#     ids=[str(uuid.uuid4()) for _ in UTAH_SocialMediaRegulation_policies],
#     documents=UTAH_SocialMediaRegulation_policies,
#     metadatas=[{"source": filename} for filename in os.listdir("../regulations/UTAH_SocialMediaRegulation") if filename.endswith(".txt")]
# )

# US reporting child sexual abuse
# US_reporting_child_sexual_abuse_policies = []
# for filename in os.listdir("../regulations/US_reporting_child_sexual_abuse"):
#     if filename.endswith(".txt"):
#         with open(os.path.join("../regulations/US_reporting_child_sexual_abuse", filename), "r", encoding="utf-8") as file:
#             content = file.read()
#             US_reporting_child_sexual_abuse_policies.append(f"{filename}\n{content}")
# US_reporting_child_sexual_abuse_policies: list[str] = US_reporting_child_sexual_abuse_policies
# US_reporting_child_sexual_abuse_collection.add(
#     ids=[str(uuid.uuid4()) for _ in US_reporting_child_sexual_abuse_policies],
#     documents=US_reporting_child_sexual_abuse_policies,
#     metadatas=[{"source": filename} for filename in os.listdir("../regulations/US_reporting_child_sexual_abuse") if filename.endswith(".txt")]
# )

# print(CS_CS_HB_3_collection.peek())
#
# print(EU_DSA_Regulations_collection.peek())
#
# print(SB976_POKSMAA_collection.peek())
#
# print(UTAH_SocialMediaRegulation_collection.peek())
#
# print(US_reporting_child_sexual_abuse_collection.peek())

# sample query
# Sample feature-based queries against all regulation collections

# def query_all_collections(query_text: str, top_k: int = 3):
#     collections = {
#         "CS_CS_HB_3": CS_CS_HB_3_collection,
#         "EU_DSA_Regulations": EU_DSA_Regulations_collection,
#         "SB976_POKSMAA": SB976_POKSMAA_collection,
#         "UTAH_SocialMediaRegulation": UTAH_SocialMediaRegulation_collection,
#         "US_reporting_child_sexual_abuse": US_reporting_child_sexual_abuse_collection,
#     }
#     results = {}
#     for name, coll in collections.items():
#         try:
#             res = coll.query(query_texts=[query_text], n_results=top_k)
#             results[name] = [
#                 {
#                     "doc_snippet": doc if doc else "",
#                     "source": meta.get("source") if meta else None,
#                     "distance": dist,
#                 }
#                 for doc, meta, dist in zip(
#                     res.get("documents", [[]])[0],
#                     res.get("metadatas", [[]])[0],
#                     res.get("distances", [[]])[0],
#                 )
#             ]
#         except Exception as e:
#             results[name] = [{"error": str(e)}]
#     return results

def query_collections(collection_names: list[str], query_text: str, top_k: int = 5):
    collections_map = {
        "CS_CS_HB_3": CS_CS_HB_3_collection,
        "EU_DSA": EU_DSA_Regulations_collection,
        "SB976_POKSMAA": SB976_POKSMAA_collection,
        "UTAH_SocialMediaRegulation": UTAH_SocialMediaRegulation_collection,
        "US_reporting_child_sexual_abuse": US_reporting_child_sexual_abuse_collection,
    }

    # If no list provided (empty), default to all collections
    if not collection_names:
        collection_names = list(collections_map.keys())

    results = {}
    for name in collection_names:
        collection = collections_map.get(name)
        if not collection:
            results[name] = [{"error": "Collection not found"}]
            continue
        try:
            res = collection.query(query_texts=[query_text], n_results=top_k)
            hits = [
                {
                    "doc_snippet": doc if doc else "",
                    "source": (meta or {}).get("source"),
                    "distance": dist,
                }
                for doc, meta, dist in zip(
                    res.get("documents", [[]])[0],
                    res.get("metadatas", [[]])[0],
                    res.get("distances", [[]])[0],
                )
            ]
            results[name] = hits
        except Exception as e:
            results[name] = [{"error": str(e)}]
    return results

sample_features = [
    {
        "name": "Age Verification Flow",
        "description": "Implement mandatory age gating with parental consent workflow for users under 16 including ID verification fallback."
    },
    {
        "name": "User Report CSAM",
        "description": "Add in-app one-click reporting for suspected child sexual abuse material with mandatory escalation and evidence preservation."
    },
    {
        "name": "Parental Dashboard",
        "description": "Provide guardians visibility into minor account activity, time limits, messaging controls, and content filtering."
    },
    {
        "name": "Algorithmic Transparency Notice",
        "description": "Show users why content is recommended including ranking signals and allow opting out of personalized feeds."
    },
    {
        "name": "Data Deletion Request",
        "description": "Allow users to request erasure of personal data and track fulfillment status within statutory timeframe."
    },
    {
        "name": "Risk Assessment Logging",
        "description": "Framework to record systemic risk assessments for platform features and mitigation actions."
    },
]

if __name__ == "__main__":
    for feat in sample_features:
        query_text = f"Feature: {feat['name']}\nDescription: {feat['description']}"
        print(f"\n==== Querying regulations for feature: {feat['name']} ====")
        feature_results = query_collections(query_text, top_k=2)
        for collection_name, hits in feature_results.items():
            print(f"\nCollection: {collection_name}")
            for i, hit in enumerate(hits, 1):
                if "error" in hit:
                    print(f"  Error: {hit['error']}")
                else:
                    print(f"  Result {i}: source={hit['source']} distance={hit['distance']:.4f}")
                    print(f"    {hit['doc_snippet']}")