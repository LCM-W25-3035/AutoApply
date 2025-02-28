# Reference: 
# (OpenAI first prompt, 2025): I'm going to work with ollama, and I have to create an agent that studies columns like Job description, Must have skills, Nice to have skills from the data, and start asking questions to the user who wants to apply for that type of jobs to build a Master resume 
# (OpenAI last prompt, 2025): Change the entries for the json loaded with the key: technical skills

from openai import OpenAI
import json
import logging
from collections import Counter

# Connect with Ollama
client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',
)

# Cargar datos desde JSON
with open("src/ai_agents/ats_agent/data_test/resume.json", "r") as file:
    cv_data = json.load(file)

with open("src/ai_agents/ats_agent/data_test/job_posting.json", "r") as file:
    job_data = json.load(file)

# Obtener skills del usuario y del job posting
cv_skills = set(cv_data.get("technical_skills", []))
job_skills = set(job_data.get("technical_skills", []))

# Identificar skills faltantes
missing_skills = list(job_skills - cv_skills)[:5]  # Limitar a 5

save_answers = {}

for skill in missing_skills:
    print(f"Do you have experience with {skill}? (yes/no)")
    answer = input("Your answer: ").strip().lower()
    
    if answer == "yes":
        while True:
            detail = input(f"Describe your experience with {skill}, including how you obtained it and a metric or result achieved: ")

            # Validar con Ollama
            validation_prompt = (
                 f"Analyze the following answer and determine if it clearly explains how the experience in {skill} was obtained "
                        f"and whether it includes a quantifiable metric or outcome. If it is insufficient, suggest improvements using action verbs and metrics:\n\n"
                        f"Answer: {detail}")
        

            response = client.chat.completions.create(
                model="llama3.2:3b",
                messages=[{"role": "user", "content": validation_prompt}],
                max_tokens=500,
                temperature=0.7,
            )

            feedback = response.choices[0].message.content.strip()

            if "correct" in feedback.lower() or "sufficient" in feedback.lower():
                save_answers[skill] = detail
                break
            elif "improved answer:" in feedback.lower():
                save_answers[skill] = feedback.replace("Improved answer:", "").strip()
                break
            else:
                print(f"Your answer needs improvement: {feedback}")
                print("Please try again with more detail using action verbs and metrics.")

# Guardar respuestas en un archivo
with open("user_answers.json", "w") as file:
    json.dump(save_answers, file, indent=4)

print("Answers saved successfully.")