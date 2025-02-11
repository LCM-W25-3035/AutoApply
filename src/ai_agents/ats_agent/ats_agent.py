from openai import OpenAI
import logging
import pandas as pd
from collections import Counter

# Connect with Ollama
client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',
)

# Load job dataset
file_path = r'D:\Big Data\Term 3\1. Big Data Capstone Project\updated_job_dataset.csv'
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

# Display questions to the user and control flow
save_answers = {}
index = 0
total_questions = len(top_skills)

while index < total_questions:
    for i in range(3):  # Ask 3 questions in each iteration
        if index < total_questions:
            skill = top_skills[index]
            print(f"Do you have experience with {skill}? (yes/no)")
            answer = input("Your answer: ").strip().lower()
            
            if answer == "yes":
                while True:
                    detail = input(f"Describe your experience with {skill}, including how you obtained it and a metric or result achieved: ")
                    
                    # Send response to Ollama for validation
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
                    
                    feedback = response.choices[0].message.content
                    if "correct" in feedback.lower() or "sufficient" in feedback.lower():
                        save_answers[skill] = detail
                        break
                    else:
                        print(f"Your answer needs improvement: {feedback}")
                        print("Please try again with more detail using action verbs and metrics.")
            
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

