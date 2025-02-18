
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

client = OpenAI(
base_url='http://localhost:11434/v1/',
api_key='ollama',)

# Input and output file paths
input_file = "src\data_gathering\Jobs-Data_Cleaned.csv.csv"
output_file = "src\data_gathering\updated_job_dataset.csv"

# Check if input file exists
if not os.path.isfile(input_file):
    raise FileNotFoundError(f"The file '{input_file}' does not exist.")

# Read the dataset
df = pd.read_csv(input_file)

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
    must_have = extract_field(content, "Must-have skills")
    nice_to_have = extract_field(content, "Nice-to-have skills")
    experience_level = extract_field(content, "Experience Level")
    contract_type = extract_field(content, "Type of Contract")
    education_level = extract_field(content, "Education level")

    return must_have, nice_to_have, experience_level, contract_type, education_level


# Function to process a single job description
def process_job_description(description: str):
    if pd.isna(description) or not description.strip():
        return "N/A", "N/A", "N/A", "N/A"

    # Example usage of a local OLlama endpoint with your custom client
    try:
        response = client.chat.completions.create(
            model="llama3",
            messages=[{"role": "system",
                       "content": ("You are a data assistant who is able to understand french and english. "
                                    "Extract and categorize the information from the following job description. "
                                    "Separate the details into the following categories:\n"
                                    "1. Must-have skills (technical skills explicitly required in the description).\n"
                                    "2. Nice-to-have skills (other skills that are preferred but not mandatory like softs skills ).\n"
                                    "3. Experience Level (categorize as 'Junior' (< 3 years), 'Mid-level' (3-8 years), or 'Senior' (> 8 years)).\n"
                                    "4. Type of Contract (e.g., 'Full-Time', 'Part-Time', 'Contract', or 'Internship').\n"
                                    "5. Education level (Level of the educations required in the job description).\n"
                                    "Return the output in EXACTLY this format in English (each category in its own line, no empty lines):\n"
                                    "Must-have skills: <list of technical skills, comma-separated>\n"
                                    "Nice-to-have skills: <list of additional skills, comma-separated>\n"
                                    "Experience Level: <Junior / Mid-level / Senior>\n"
                                    "Type of Contract: <Full-Time / Part-Time / Contract / Internship>\n"
                                    "Education level: <Level of the educations required>"
                                        )},
                        {"role": "user", "content":  f"Job Description:\n{description}"},
                    ],
            max_tokens=2500,
            temperature=0.7
        )
        
        # OLlama-style response (similar to OpenAI):
        content = response.choices[0].message.content
        print("Raw Content:", content) 
        return parse_raw_content(content)

    except Exception as e:
        logging.error(f"Error extracting details: {e}")
        return "N/A", "N/A", "N/A", "N/A"

# Initialize new columns
df["Must-have Skills"] = "N/A"
df["Nice-to-have Skills"] = "N/A"
df["Experience Level"] = "N/A"
df["Type of Contract"] = "N/A"
df["Education level"] = "N/A"

# Process each job description
df[["Must-have Skills", "Nice-to-have Skills", "Experience Level", "Type of Contract", "Education level"]] = (
    df["Job Description"].apply(lambda desc: pd.Series(process_job_description(desc)))
)

# Save the updated dataset
df.to_csv(output_file, index=False, encoding="utf-8")

end_time = time.time()

print(f"Time taken: {end_time - start_time:.2f} seconds")

print(f"Updated dataset saved to: {output_file}")
