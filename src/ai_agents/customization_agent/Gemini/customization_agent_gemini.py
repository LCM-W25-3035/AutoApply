# Reference
# (OpenAI, ChatGPT o1, first prompt, 2025): Now I will create a version of the agent conecting with Gemini API, give me the example to call Gemini insted of Llama
# (OpenAI, ChatGPT o1, last prompt, 2025): There is an error with genai.client

import logging
import json
import google.generativeai as genai

# Set your Gemini API key here
GEMINI_API_KEY = "KEY"

# Configure the API key once at the start
genai.configure(api_key=GEMINI_API_KEY)

def send_prompt_to_gemini(prompt, max_tokens=1500):
    """
    Sends a prompt to the Gemini API using google.generativeai and returns the response as text.
    """
    try:
        model = genai.GenerativeModel(
            'gemini-2.0-flash',  # Update with the correct Gemini model name if needed
            generation_config={'max_output_tokens': max_tokens}
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Error querying Gemini API: {e}")
        return ""

def extract_json(text):
    """
    Extracts the JSON portion from a given text by locating the first '{' and last '}'.
    Returns the substring if found, otherwise returns the original text.
    """
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        return text[start:end+1]
    return text

def customize_cv(cv_json: dict, job_offer_json: dict) -> dict:
    """
    Customizes the CV based on the extracted CV data and the job offer data.
    Both inputs are dictionaries parsed from JSON.
    
    The output JSON should include all important personal details (Name, Email, Phone, SocialMedia)
    along with a structured breakdown:
      - "Summary": <Rewritten summary text>,
      - "Skills": <Rewritten skills text>,
      - "Experience": [ { "Company": <Company name>, "Dates": <Start date - End date>, "Functions": <Rewritten description> }, ... ],
      - "Education": [ { "Institution": <Institution name>, "Dates": <Start date - End date>, "Degree": <Degree obtained> }, ... ]
      
    Do not invent new content; only enhance and reorganize the existing information.
    """
    original_cv = cv_json.get("raw_text", "")
    job_description = json.dumps(job_offer_json, indent=2)
    
    prompt = f"""
Using the following inputs, generate a revised version of the CV that improves the wording and structure to clearly emphasize the candidate's relevant skills and experiences for the job offer.
Do not invent any new content; only enhance and reorganize the existing information.

Original CV:
{original_cv}

Job Offer:
{job_description}

Please output the rewritten CV in a structured JSON format with the following keys:

{{
  "PersonalInfo": {{
      "Name": "<Candidate's full name>",
      "Email": "<Candidate's email address>",
      "Phone": "<Candidate's phone number>",
      "SocialMedia": "<Links to social media profiles or other contact details>"
  }},
  "Summary": "<Rewritten summary text>",
  "Skills": "<Rewritten skills text>",
  "Experience": [
    {{
      "Company": "<Company name>",
      "Dates": "<Start date - End date>",
      "Functions": "<Rewritten description of responsibilities and functions>"
    }}
  ],
  "Education": [
    {{
      "Institution": "<Institution name>",
      "Dates": "<Start date - End date>",
      "Degree": "<Degree obtained>"
    }}
  ]
}}

Ensure the JSON is valid.
"""
    result = send_prompt_to_gemini(prompt, max_tokens=1500)  # try lowering tokens if needed
    logging.info("Raw customization result:")
    logging.info(result)
    
    # Extract JSON part from the response
    result_json_str = extract_json(result)
    try:
        return json.loads(result_json_str)
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON from customization output.")
        return {"error": "Invalid JSON output from customization agent"}
