from docx import Document
import ollama
import pandas as pd

doc = Document(r'C:\CAROL\job_recommender\Carol D Samson.docx')
full_text = " ".join([para.text for para in doc.paragraphs])

#print(full_text)


data = full_text

# Using ollama's chat method for getting a response from the model 'mistral'. Temperature option is also provided.
ollama_response = ollama.chat(model='mistral', messages=[
  {
    'role': 'system',
    'content': 'You are a helpful assistant.',
  },
  {
    'role': 'user',
    'content': f'Please extract name, title, skills, education, years of experience from this resume and output as JSON: \n\n {data}',
  },
],
options = {
  'temperature': 1.5, # very creative
  #'temperature': 0 # very conservative
})

# Printing the response from ollama.
print(ollama_response['message']['content'])

#output_file = "resume_analysis_results.csv"
#extracted_text = ollama_response['message']['content']

#for line in extracted_text.splitlines():
#    print(line)

#df.to_csv(output_file, index=False)

