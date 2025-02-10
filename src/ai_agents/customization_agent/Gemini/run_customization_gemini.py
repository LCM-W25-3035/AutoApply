import asyncio
import json
import os
from customization_agent_gemini import customize_cv

def filter_empty_keys(data):
    """
    Recursively filters out keys with empty values (None, empty string, empty list, or empty dict)
    from dictionaries and lists.
    """
    if isinstance(data, dict):
        return {k: filter_empty_keys(v) for k, v in data.items() if v not in [None, "", [], {}]}
    elif isinstance(data, list):
        return [filter_empty_keys(item) for item in data if item not in [None, "", [], {}]]
    else:
        return data

# Define the input file paths (JSON outputs from the extractor and matcher agents)
cv_input_filepath = os.path.join("src", "ai_agents", "pdf_extractor_agent", "extractor_output_3.json")
job_offer_input_filepath = os.path.join("src", "ai_agents", "resume_jobs_matcher_agent", "matched_jobs_for_resume_3.json")
output_json_filepath = os.path.join("src", "ai_agents", "customization_agent", "Gemini", "customized_cv_output.json")

async def run_customization():
    try:
        with open(cv_input_filepath, "r", encoding="utf-8") as f:
            cv_data = json.load(f)
        with open(job_offer_input_filepath, "r", encoding="utf-8") as f:
            matcher_data = json.load(f)
        job_offer_data = matcher_data.get("matched_jobs", [])[0] if matcher_data.get("matched_jobs") else {}
        
        customized_cv = customize_cv(cv_data, job_offer_data)
        filtered_customized_cv = filter_empty_keys(customized_cv)
        
        print("Customized CV:")
        print(json.dumps(filtered_customized_cv, ensure_ascii=False, indent=4))
        
        with open(output_json_filepath, "w", encoding="utf-8") as f:
            json.dump(filtered_customized_cv, f, ensure_ascii=False, indent=4)
        
        print(f"Customized CV output saved at: {output_json_filepath}")
    
    except Exception as e:
        print(f"Error during customization: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_customization())
