import openai
import requests
import logging
import json

# Ollama API configuration for Llama
openai.api_base = "http://localhost:11434/v1"
openai.api_key = "ollama"

def send_prompt_to_ollama(prompt, max_tokens=1500):
    """
    Sends a prompt to Ollama (Llama) and returns the response as text.
    """
    url = f"{openai.api_base}/completions"
    payload = {
        "model": "llama3.1:8b",
        "prompt": prompt,
        "max_tokens": max_tokens
    }
    headers = {"Content-Type": "application/json"}
    try:
        logging.info("Sending prompt to Ollama:")
        logging.info(prompt)
        response = requests.post(url, json=payload, headers=headers, timeout=480)
        response.raise_for_status()
        result = response.json()
        text = result.get("text", "").strip()
        if not text and "choices" in result:
            text = result["choices"][0].get("text", "").strip()
        return text
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error: {http_err}")
        if response in locals():
            logging.error(f"Server response: {response.text}")
        return ""
    except requests.exceptions.RequestException as req_err:
        logging.error(f"Request error to Ollama: {req_err}")
        return ""

def extract_json(text: str) -> str:
    """
    Extracts the JSON portion from a text by locating the first '{' and the last '}'.
    Returns the substring if found; otherwise, returns the original text.
    """
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
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
    result = send_prompt_to_ollama(prompt, max_tokens=2500)
    logging.info("Raw customization result:")
    logging.info(result)
    
    # Extraer la parte JSON del resultado (por si incluye texto adicional)
    result_json_str = extract_json(result)
    try:
        return json.loads(result_json_str)
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON from customization output.")
        return {"error": "Invalid JSON output from customization agent"}
