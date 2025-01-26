import pandas as pd
from typing import Dict, Any, List
from Model_Mya_V1.base_agent import BaseAgent
import json

class MatcherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Matcher",
            instructions="""Match candidate profiles with job positions.
            Consider: skills match, experience level.
            Provide detailed reasoning and compatibility scores.
            Return matches in JSON format with title, match_score, and other details.""",
        )
        # Path to jobs data CSV
        self.jobs_file_path = "jobs_data_sample.csv"

    async def run(self, messages: list) -> Dict[str, Any]:
        """Match candidate with available job positions based on skills and experience level"""
        print("🎯 Matcher: Finding suitable job matches")

        try:
            # Validate message format
            if not messages or "content" not in messages[-1]:
                print("⚠️ No valid content in messages.")
                return {
                    "matched_jobs": [],
                    "match_timestamp": "2024-03-14",
                    "number_of_matches": 0,
                }

            content = messages[-1].get("content", {})

            # Convert to valid JSON
            try:
                if not isinstance(content, dict):
                    try:
                        content = json.loads(content)  # Only parse JSON if content is a string
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Error parsing JSON: {e}")
                        return {
                            "matched_jobs": [],
                            "match_timestamp": "2024-03-14",
                            "number_of_matches": 0,
                        }

                analysis_results = content  # Use directly if already a dictionary
            # Ensure valid JSON format
            except json.JSONDecodeError as e:
                print(f"⚠️ Error parsing JSON: {e}")
                return {
                    "matched_jobs": [],
                    "match_timestamp": "2024-03-14",
                    "number_of_matches": 0,
                }

        except Exception as e:
            print(f"⚠️ Unexpected error while processing messages: {e}")
            return {
                "matched_jobs": [],
                "match_timestamp": "2024-03-14",
                "number_of_matches": 0,
            }

        # Extract skills and experience level
        skills_analysis = analysis_results.get("skills_analysis", {})

        if not skills_analysis:
            print("⚠️ No skills analysis provided in the input.")
            return {
                "matched_jobs": [],
                "match_timestamp": "2024-03-14",
                "number_of_matches": 0,
            }

        # Extract technical skills and experience level
        skills = skills_analysis.get("technical_skills", [])
        experience_level = skills_analysis.get("experience_level", "Mid-level")

        if not isinstance(skills, list) or not skills:
            print("⚠️ No valid skills found, defaulting to an empty list.")
            skills = []

        if experience_level not in ["Junior", "Mid-level", "Senior"]:
            print("⚠️ Invalid experience level detected, defaulting to Mid-level.")
            experience_level = "Mid-level"

        print(f" ==>>> Skills: {skills}, Experience Level: {experience_level}")

        # Search jobs from CSV file
        matching_jobs = self.search_jobs(skills, experience_level)

        # Calculate match scores
        scored_jobs = []
        for job in matching_jobs:
            try:
                required_skills = set(job["requirements"])
                candidate_skills = set(skills)
                overlap = len(required_skills.intersection(candidate_skills))
                total_required = len(required_skills)

                match_score = int((overlap / total_required) * 100) if total_required > 0 else 0

                # Include jobs with >10% match
                if match_score >= 10:
                    scored_jobs.append(
                        {
                            "title": f"{job.get('title', 'No Title')} at {job.get('company', 'Unknown Company')}",
                            "match_score": f"{match_score}%",
                            "salary_range": job.get("salary_range", "Not Specified"),
                            "requirements": job["requirements"],
                        }
                    )
            except Exception as e:
                print(f"⚠️ Error calculating match score: {e}")

        print(f" ==>>> Scored Jobs: {scored_jobs}")

        # Sort by match score
        scored_jobs.sort(key=lambda x: int(x["match_score"].rstrip("%")), reverse=True)

        return {
            "matched_jobs": scored_jobs[:3],  # Return top 3 matches
            "match_timestamp": "2024-03-14",
            "number_of_matches": len(scored_jobs),
        }

    def search_jobs(self, skills: List[str], experience_level: str) -> List[Dict[str, Any]]:
        """Search jobs based on skills and experience level using CSV file"""
        try:
            # Load job data from CSV file
            jobs_df = pd.read_csv(self.jobs_file_path)

            # Ensure required columns exist
            required_columns = ["title", "company", "salary_range", "experience_level", "requirements"]
            missing_columns = [col for col in required_columns if col not in jobs_df.columns]

            if missing_columns:
                print(f"⚠️ CSV file is missing required columns: {missing_columns}")
                return []

            # Filter jobs by experience level
            filtered_jobs = jobs_df[jobs_df["experience_level"] == experience_level]

            # Now filter jobs based on skills matching the requirements column
            matching_jobs = []
            for _, row in filtered_jobs.iterrows():
                try:
                    # Ensure requirements column is not null
                    if pd.isna(row["requirements"]):
                        continue  # Skip jobs with missing requirements

                    # Split the requirements string into a list of skills
                    job_requirements = [skill.strip() for skill in row["requirements"].split(",")]

                    # Check if any of the candidate's skills match the job requirements
                    if any(skill in job_requirements for skill in skills):
                        matching_jobs.append({
                            "title": row["title"],
                            "company": row["company"],
                            "salary_range": row["salary_range"],
                            "experience_level": row["experience_level"],
                            "requirements": job_requirements
                        })
                except Exception as e:
                    print(f"⚠️ Error processing job entry: {e}")

            return matching_jobs

        except Exception as e:
            print(f"⚠️ Error searching jobs in CSV file: {e}")
            return []
