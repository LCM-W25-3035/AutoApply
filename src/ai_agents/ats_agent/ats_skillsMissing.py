# Reference: 
# (OpenAI first prompt, 2025): I'm working with gemini to have the agent evaluate the missing skills and if the user has them (answer yes), help them evaluate and build a report of their experience with actions verb and metrics. This is the prompt I have, how can I improve it?
    #prompt:  f"Analyze the following answer and determine if it clearly explains how the experience in {skill} was obtained "
    #                   f"and whether it includes a quantifiable metric or outcome. If it is insufficient, suggest improvements using action verbs and metrics:\n\n"
    #                   f"Answer: {detail}")
# (OpenAI last prompt, 2025): The idea is that the suggestion you want with an example of how the answer should be

import google.generativeai as genai
import json
import re  # Import regex

# Configure Gemini API
API_KEY = ""
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')
save_answers = {}

# Load data from JSON
with open("src/ai_agents/ats_agent/data_test/resume.json", "r") as file:
    cv_data = json.load(file)

with open("src/ai_agents/ats_agent/data_test/job_posting.json", "r") as file:
    job_data = json.load(file)

# Extract skills from resume and job posting
cv_skills = set(cv_data.get("technical_skills", []))
job_skills = set(job_data.get("technical_skills", []))

# Identify missing skills (limit to 5)
missing_skills = list(job_skills - cv_skills)[:5]

for skill in missing_skills:
    print(f"Do you have experience with {skill}? (yes/no)")
    answer = input("Your answer: ").strip().lower()

    if answer == "yes":
        while True:
            # Ask the user to describe their experience with the skill
            detail = input(f"Describe your experience with {skill}, including how you obtained it and a metric or result achieved: ")

            # Validate the response with Gemini
            validation_prompt = (
                f"Evaluate the following response regarding experience with {skill}. "
                f"Ensure it includes:\n"
                f"- A clear explanation of how the experience was obtained.\n"
                f"- At least one action verb describing what was done.\n"
                f"- A quantifiable metric or measurable impact.\n\n"
                f"Response to evaluate:\n{detail}\n\n"
                f"### Evaluation Criteria ###\n"
                f"- If the response meets all criteria, return: 'Evaluation: ✅ Strong response.'\n"
                f"- If the response is missing details, return: 'Evaluation: ❌ Needs improvement.' "
                f"and provide a suggestion with an example of how the response should be structured.\n\n"
                f"### Example of a strong response ###\n"
                f"'Implemented a predictive maintenance system using Python, reducing machine downtime by 25% over six months.'\n\n"
            )

            try:
                response = model.generate_content(validation_prompt)
                feedback = response.text.strip()
                print("\n🔹 Gemini Response:\n", feedback)  # Display Gemini's response for debugging

                # If the response is strong, save it and exit the loop
                if re.search(r"✅ Strong response", feedback, re.IGNORECASE):
                    save_answers[skill] = detail
                    break

                # If the response needs improvement, show feedback and an example
                if re.search(r"❌ Needs improvement", feedback, re.IGNORECASE):
                    print("\n⚠️ Your answer needs improvement.")

                    # Extract a strong response example from Gemini's feedback
                    example_match = re.search(r"Example of a strong response:\s*(.+)", feedback, re.IGNORECASE)
                    if example_match:
                        print(f"\n🔄 Example of how you should structure your answer:\n{example_match.group(1).strip()}")

                    print("\nPlease try again with more detail using action verbs and metrics.")

            except Exception as e:
                print(f"\n❌ Error communicating with Gemini: {e}")
                print("Skipping this skill...")
                break

# Save responses to a JSON file
with open("user_answers.json", "w") as file:
    json.dump(save_answers, file, indent=4)

print("\n✅ Answers saved successfully.")
