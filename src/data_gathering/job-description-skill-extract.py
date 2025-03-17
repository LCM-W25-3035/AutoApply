
"""

OpenAi GPT 4o
Prompt 1: I have a dataset of jobs offers, the dataset has 7 columns and one of those is job description
 each record contain information about the jobs in text that means unstructured data (I think Correct me 
 if im wrong) so, I want to create a couple of columns more eith this information -
   Skill (Must-have → technical, Nice-to-have → other skills. Put comma in between please)
- Experience Level (e.g., "Junior" < 3 years, "Mid-level" 3-8 years, "Senior" > 8 years)
- Type (Contract, Full-Time, Part-Time, Internship), so i dont know if is better leveraing the 
LLM models or try to do it or other site what are my choices

"""

import pandas as pd
import os
import logging
import re
from openai import OpenAI
import time

start_time = time.time()

var_experience_level = "Experience Level"
var_tipe_of_contract = "Type of Contract"
var_education_level = "Education level"

client = OpenAI(
base_url='http://localhost:11434/v1/',
api_key='ollama',)

# Input and output file paths
input_file = "glassdoor_jobs_dataAnalysisQuebec.csv"
output_file = "updated_job_dataset.csv"

# Check if input file exists
if not os.path.isfile(input_file):
    raise FileNotFoundError(f"The file '{input_file}' does not exist.")

# Read the dataset
df = pd.read_csv(input_file, encoding='utf-8-sig')

# Validate necessary columns
if "Job Description" not in df.columns:
    raise ValueError("The 'Job Description' column is missing in the file.")

def extract_field(content, label):
    """
    Regex pattern to capture exactly one line of text after the label.
    e.g. label = 'Must-have skills', we look for:
       'Must-have skills: ...some text up to newline...'
    """
    pattern = rf"{label}[:\s]*([^\n]+)"
    match = re.search(pattern, content, re.IGNORECASE)
    return match.group(1).strip() if match else "N/A"

def parse_raw_content(content: str):
    """
    Parses the raw content to extract structured data from lines that look like:
      Must-have skills: ...
      Nice-to-have skills: ...
      Experience Level: ...
      Type of Contract: ...
      Education level: ...
    """
    keywords = extract_field(content, "Keywords")
    must_have = extract_field(content, "Must-have skills")
    nice_to_have = extract_field(content, "Nice-to-have skills")
    experience_level = extract_field(content, var_experience_level)
    contract_type = extract_field(content, var_tipe_of_contract)
    education_level = extract_field(content, var_education_level)

    return keywords, must_have, nice_to_have, experience_level, contract_type, education_level


# Function to process a single job description
def process_job_description(description: str):
    if pd.isna(description) or not description.strip():
        return "N/A", "N/A", "N/A", "N/A", "N/A","N/A"

    # Example usage of a local OLlama endpoint with your custom client
    try:
        response = client.chat.completions.create(
        model="oscar",
        messages=[
            {"role": "system",
             "content": (
                "You are a data assistant who is able to understand French and English. "
                "Extract and categorize the information from the following job description. "
                "Separate the details into the following categories:\n"
                "1. keywords (list of keyword and skills that you think is important to find or match this job descriptios).\n"
                "2. Must-have skills (technical skills and keywords explicitly required in the description).\n"
                "3. Nice-to-have skills (other skills that are preferred but not mandatory, including soft skills).\n"
                "4. Experience Level (categorize as 'Junior' (< 3 years), 'Mid-level' (3-8 years), or 'Senior' (> 8 years)).\n"
                "5. Type of Contract (e.g., 'Full-Time', 'Part-Time', 'Contract', or 'Internship').\n"
                "6. Education Level (level of education required in the job description).\n\n"
                "Return the OUTPUT in EXACTLY this format in English (each category on its own line, no empty lines):\n"
                "keyword: <list of keywords and skills to find this job, comma-separated>\n"
                "Must-have skills: <list of technical skills and keywords, comma-separated>\n"
                "Nice-to-have skills: <list of additional skills, comma-separated>\n"
                "Experience Level: <Junior / Mid-level / Senior>\n"
                "Type of Contract: <Full-Time / Part-Time / Contract / Internship>\n"
                "Education level: <education level required>\n\n"
                "Do not add any explanation or extra comments. Respond only with the categorized output."
                "IMPORTANT\n"
                "Use this exact structure."
                "If any category is not mentioned in the description, write Not specified\n"
                "Do not return anything outside of this format.")},
            {"role": "user",
            "content": f"Job Description:\n{description}"
            }],
        max_tokens=1500,
        temperature=0.4)
        
        # OLlama-style response (similar to OpenAI):
        content = response.choices[0].message.content
        print("Raw Content:", content) 
        return parse_raw_content(content)

    except Exception as e:
        logging.error(f"Error extracting details: {e}")
        return "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"

# Initialize new columns
df["keywordss"] = "N/A"
df["Must-have Skills"] = "N/A"
df["Nice-to-have Skills"] = "N/A"
df[var_experience_level] = "N/A"
df[var_tipe_of_contract] = "N/A"
df[var_education_level] = "N/A"

# Process each job description
df[["keywordss","Must-have Skills", "Nice-to-have Skills", "Experience Level", "Type of Contract", "Education level"]] = (
df[["Must-have Skills", "Nice-to-have Skills", var_experience_level, var_tipe_of_contract, var_education_level]] = (
    df["Job Description"].apply(lambda desc: pd.Series(process_job_description(desc)))
)

# Save the updated dataset
df.to_csv(output_file, index=False, encoding="utf-8")

end_time = time.time()

print(f"Time taken: {end_time - start_time:.2f} seconds")

print(f"Updated dataset saved to: {output_file}")