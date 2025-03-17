import google.generativeai as genai
import json
import re  

# Configure Gemini API
API_KEY = ""
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Load JSON data
def load_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

# Load the resume data
file_path = "src/ai_agents/ats_agent/data_test/esume_delete_experience_not_relate_.json"
resume_data = load_json(file_path)
work_experience = resume_data.get("work_experience", [])

# Function to validate achievements with Gemini
def validate_with_gemini(skill, detail):
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
            improved_response_match = re.search(r"Example:\s*(.+)", feedback, re.IGNORECASE)
            if improved_response_match:
                example = improved_response_match.group(1).strip()
            else:
                example = "Ensure you include a percentage or numerical value, such as 'Reduced processing time by 30%' or 'Led a team of 5 engineers'."
            return False, example
    except Exception as e:
        print(f"Error communicating with Gemini: {e}")
        return False, "Ensure you include a percentage or numerical value."

# Process achievements and validate them
for job in work_experience:
    print(f"\nEvaluating achievements for: {job['job_title']} at {job['company']}\n")
    for i, achievement in enumerate(job["achievement"]):
        while True:
            is_valid, feedback = validate_with_gemini(job['job_title'], achievement)
            if is_valid:
                print(f"✅ Valid achievement: {achievement}")
                break
            else:
                print(f"\n❌ Needs improvement: {achievement}")
                print(f"Suggested improvement: {feedback}")
                achievement = input("Please rewrite the achievement with improvements: ")
        
        # Save the validated achievement
        job["achievement"][i] = achievement

# Save the updated JSON file
output_file = "resume_updated.json"
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(resume_data, file, indent=4, ensure_ascii=False)

print(f"\nAll achievements validated and saved in '{output_file}'.")
