from openai import OpenAI
import logging
import pandas as pd
import json
from collections import Counter

# Connect with Ollama
client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',
)

# Load Database from CSV
file_path = 'src/ai_agents/ats_agent/data/cleaned_job_dataset.csv'
df = pd.read_csv(file_path)

# Extract and count the most mentioned skills (must-have and nice-to-have combined)
skills = []
for _, row in df.iterrows():
    if not pd.isna(row["Must-have Skills"]):
        skills.extend(row["Must-have Skills"].split(", "))
    if not pd.isna(row["Nice-to-have Skills"]):
        skills.extend(row["Nice-to-have Skills"].split(", "))

skill_counter = Counter(skills)

# Get the 20 most mentioned skills
top_skills = [skill for skill, _ in skill_counter.most_common(20)]

# Print the top 20 skills before proceeding
print("Top 20 most mentioned skills:")
for skill in top_skills:
    print(f"- {skill}")

input("Press Enter to continue...")

# Load user's existing skills from JSON file
with open("src/ai_agents/resume_analyzer_agent/analyzer_output_1.json", "r") as file:
    user_data = json.load(file)

user_skills = set(user_data["skills_analysis"]["technical_skills"]["other_skills"])

# Determine which skills the user does not have
missing_skills = [skill for skill in top_skills if skill not in user_skills]

# Display questions to the user and control flow
save_answers = {}
index = 0
total_questions = len(missing_skills)

while index < total_questions:
    for i in range(3):  # Ask 3 questions in each iteration
        if index < total_questions:
            skill = missing_skills[index]
            while True:
                print(f"Do you have experience with {skill}? (yes/no)")
                answer = input("Your answer: ").strip().lower()
                
                if answer in ["yes", "no"]:
                    break
                else:
                    print("Invalid response. Please answer with 'yes' or 'no'.")
            
            if answer == "yes":
                while True:
                    detail = input(f"Describe your experience with {skill}, including how you obtained it and a metric or result achieved: ")
                    
                    # Send response to Ollama for validation
                    validation_prompt = (
                        f"Analyze the following answer and check if it contains both an action verb and a quantifiable metric. "
                        f"If both elements are present, respond with 'valid response'. Otherwise, provide feedback on how to improve it using action verbs and metrics:\n\n"
                        f"Answer: {detail}")
                    
                    response = client.chat.completions.create(
                        model="llama3.2:3b",
                        messages=[{"role": "user", "content": validation_prompt}],
                        max_tokens=500,
                        temperature=0.7,
                    )
                    
                    feedback = response.choices[0].message.content.lower()
                    
                    if "valid response" in feedback:
                        save_answers[skill] = detail
                        print("Response accepted.")
                        break
                    else:
                        print(f"Your answer needs improvement: {feedback}")
                        print("Ensure your response includes an action verb and a metric. Please try again.")
            
            index += 1
    
    if index >= total_questions:
        break
    
    continue_prompt = input("Do you want to continue with more questions? (yes/no): ").strip().lower()
    if continue_prompt != 'yes':
        break

# Save answers in a dictionary
with open("user_answers.txt", "w") as file:
    for skill, detail in save_answers.items():
        file.write(f"Skill: {skill}\nExperience: {detail}\n\n")

print("Answers saved successfully.")