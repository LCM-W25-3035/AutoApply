# Reference: 
# (OpenAI first prompt, 2025): I'm working with gemini to have the agent evaluate the missing skills and if the user has them (answer yes), help them evaluate and build a report of their experience with actions verb and metrics. This is the prompt I have, how can I improve it?
    #prompt:  f"Analyze the following answer and determine if it clearly explains how the experience in {skill} was obtained "
    #                   f"and whether it includes a quantifiable metric or outcome. If it is insufficient, suggest improvements using action verbs and metrics:\n\n"
    #                   f"Answer: {detail}")
# (OpenAI last prompt, 2025): I'm going to include the company key within the experience to ask the user which company they obtained it from before saving the skills in the user answer json.

import google.generativeai as genai
import json
import re  

# Configure Gemini API
API_KEY = ""
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Dictionary to store user responses
save_answers = {}

# Load data from JSON
def load_json(file_path):
    """Loads JSON data from a file."""
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

cv_data = load_json("src/ai_agents/ats_agent/data_test/resume.json")
job_data = load_json("src/ai_agents/ats_agent/data_test/job_posting.json")

# Extract skills from resume and job posting
cv_technical_skills = set(cv_data.get("technical_skills", []))
job_technical_skills = set(job_data.get("technical_skills", []))

cv_soft_skills = set(cv_data.get("soft_skills", []))
job_soft_skills = set(job_data.get("soft_skills", []))

# skills that are **in the job posting** but **not in the resume**
missing_technical_skills = list(job_technical_skills - cv_technical_skills)[:5]
missing_soft_skills = list(job_soft_skills - cv_soft_skills)[:5]

# Extract company names from work experience
companies = list({exp["company"] for exp in cv_data.get("work_experience", [])})

# Create a JSON file with missing skills
missing_skills = {
    "technical_skills": missing_technical_skills,
    "soft_skills": missing_soft_skills
}

# Save missing skills to a JSON file
with open("skills_missing.json", "w") as file:
    json.dump(missing_skills, file, indent=4)
print("Skills missing saved in 'skills_missing.json'.")

def validate_with_gemini(skill, detail):
    """Validates the user's response using the Gemini API and ensures a corrected example is always provided."""
    validation_prompt = (
        f"Evaluate the following response regarding experience with {skill}. "
        f"Ensure it includes:\n"
        f"- A clear explanation of how the experience was obtained.\n"
        f"- At least one action verb describing what was done.\n"
        f"- At least one quantifiable metric or measurable impact, which can be either:\n"
        f"  - A percentage improvement (e.g., 'Increased efficiency by 25%').\n"
        f"  - A numerical value (e.g., 'Led a team of 10 engineers').\n\n"
        f"Response to evaluate:\n{detail}\n\n"
        f"### Evaluation Criteria ###\n"
        f"- If the response meets all criteria, return: 'Evaluation: ✅ Strong response.'\n"
        f"- If the response is missing details, return: 'Evaluation: ❌ Needs improvement.' "
        f"and provide a rewritten version of the response following a strong format.\n\n"
        f"### Example of a strong response ###\n"
        f"'Implemented a predictive maintenance system using Python, reducing machine downtime by 25% over six months.'\n"
        f"'Led a team of 10 engineers in developing an AI-driven analytics tool, improving operational efficiency by 20%.'\n\n"
        f"Now, if the response needs improvement, provide a corrected version formatted as:\n"
        f"'Example: [Your improved response here]'"
    )

    try:
        response = model.generate_content(validation_prompt)
        feedback = response.text.strip()

        if "✅ Strong response" in feedback:
            return True, feedback

        elif "❌ Needs improvement" in feedback:
            # Extract an improved response using different patterns
            improved_response_match = re.search(r"Example:\s*(.+)", feedback, re.IGNORECASE)

            if improved_response_match:
                example = improved_response_match.group(1).strip()
            else:
                # Provide a default structured example if Gemini fails
                example = (
                    "For example, instead of saying 'I worked with this tool', you could say:\n"
                    "'Designed interactive Power BI dashboards for business intelligence, "
                    "leading to a 20% reduction in report generation time.'"
                )

            return False, example

    except Exception as e:
        print(f"Error communicating with Gemini: {e}")
        return False, "Ensure you include a percentage or numerical value, such as 'Reduced processing time by 30%' or 'Led a team of 5 engineers'."


def process_missing_skills(missing_skills, skill_type):
    """Prompts the user for missing skills, asks for the company, and validates responses with Gemini."""
    for skill in missing_skills:
        answer = input(f"Do you have experience with {skill}? (yes/no): ").strip().lower()

        if answer == "yes":
            # Display a numbered list of companies for user selection
            print("\nSelect the company where you gained experience with this skill:")
            for i, company in enumerate(companies, 1):
                print(f"{i}. {company}")

            while True:
                try:
                    company_index = int(input("Enter the number corresponding to the company: ").strip())
                    if 1 <= company_index <= len(companies):
                        selected_company = companies[company_index - 1]
                        break
                    else:
                        print("Invalid selection. Please enter a valid number from the list.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

            while True:
                detail = input(f"Describe your experience with {skill}, including how you obtained it and a metric or result achieved: ")

                is_valid, feedback = validate_with_gemini(skill, detail)

                if is_valid:
                    if selected_company not in save_answers:
                        save_answers[selected_company] = {"technical_skills": {}, "soft_skills": {}}
                    save_answers[selected_company][skill_type][skill] = detail
                    print("Response accepted.")
                    break
                else:
                    print("Your answer needs improvement.")
                    print(f"Example: {feedback}")
                    print("Please try again with more detail.")

# Process missing technical and soft skills
process_missing_skills(missing_technical_skills, "technical_skills")
process_missing_skills(missing_soft_skills, "soft_skills")

# Save user responses to a JSON file
with open("user_answers.json", "w") as file:
    json.dump(save_answers, file, indent=4)


print("User answers saved in 'user_answers.json'.")