from typing import Dict, Any
from Models.base_agent import BaseAgent
import json  # For JSON parsing
import re  # For regex-based cleaning

class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Analyzer",
            instructions="""Analyze candidate profiles and extract:
            1. Technical skills (as a list)
            2. Years of experience (numeric)
            3. Experience level (Junior/Mid-level/Senior)      
            Format the output as structured data.""",
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Analyze the extracted resume data"""
        print("🔍 Analyzer: Analyzing candidate profile")

        extracted_data = messages[-1]["content"]

        # Ensure the extracted data is a dictionary
        if isinstance(extracted_data, str):
            # If it's a string, try to parse it into a JSON object
            try:
                extracted_data = json.loads(extracted_data)
            except json.JSONDecodeError:
                print("Error: Extracted data is not valid JSON.")
                return {
                    "skills_analysis": {},
                    "analysis_timestamp": "2024-03-14",
                    "confidence_score": 0.5,
                }

        # Retrieve the structured data (resume's key sections)
        structured_data = extracted_data.get("structured_data", "")
        
        if not structured_data:
            print("Error: 'structured_data' key is missing in extracted data.")
            return {
                "skills_analysis": {},
                "analysis_timestamp": "2024-03-14",
                "confidence_score": 0.5,
            }

        # Step 1: Clean and extract relevant details from structured_data using regex (manual parsing)
        skills = self.extract_skills(structured_data)
        experience = self.extract_experience(structured_data)

        # Step 2: Return a structured JSON object with the extracted details
        analysis_result = {
            "technical_skills": skills,
            "years_of_experience": experience,
            "experience_level": "Mid-level",  # This can be inferred from experience or added manually
        }

        return {
            "skills_analysis": analysis_result,
            "analysis_timestamp": "2024-03-14",
            "confidence_score": 0.85,
        }

    def extract_skills(self, structured_data: str):
        """Extract skills using regex or simple string matching"""
        skill_keywords = [
            "Python", "Java", "SQL", "JavaScript", "C", "C++", "R", "Ruby", "Swift", "Go", "Kotlin", "PHP", "HTML", "CSS", "TypeScript",
            "Node.js", "React", "Angular", "Vue.js", "jQuery", "Django", "Flask", "Spring", "Laravel", "ASP.NET", "Ruby on Rails",
            "Machine Learning", "Deep Learning", "Artificial Intelligence", "TensorFlow", "Keras", "PyTorch", "Scikit-learn", "XGBoost",
            "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "CI/CD", "DevOps", "Terraform", "Ansible", "Jenkins", "Git", "GitHub", "GitLab",
            "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Oracle", "Cassandra", "Redis", "Elasticsearch", "HBase", "BigQuery", "NoSQL", "GraphQL",
            "Data Science", "Data Analysis", "Data Visualization", "Tableau", "Power BI", "Looker", "Matplotlib", "Seaborn", "Plotly", "D3.js",
            "Hadoop", "Spark", "MapReduce", "Apache Kafka", "Kafka Streams", "Flink", "Apache Storm", "ETL", "Data Warehousing",
            "Natural Language Processing", "Computer Vision", "OpenCV", "Image Processing", "Speech Recognition", "Chatbot Development", "OCR",
            "Blockchain", "Cryptocurrency", "Smart Contracts", "Ethereum", "Solidity", "IPFS", "Hyperledger", "Cryptography", "NFTs",
            "Cybersecurity", "Penetration Testing", "Ethical Hacking", "Firewalls", "SIEM", "IDS/IPS", "Malware Analysis", "Cryptanalysis",
            "Agile", "Scrum", "Kanban", "Project Management", "Jira", "Trello", "Asana", "Confluence", "Test Automation", "Unit Testing",
            "UI/UX Design", "Figma", "Adobe XD", "Sketch", "Wireframing", "Prototyping", "User Research", "A/B Testing", "Responsive Design",
            "SEO", "SEM", "Digital Marketing", "Google Analytics", "Marketing Automation", "Salesforce", "HubSpot", "PPC", "Content Management",
            "Cloud Computing", "Serverless Architecture", "Cloud Security", "Virtualization", "VMware", "Hyper-V", "Vagrant", "Terraform",
            "Networking", "TCP/IP", "DNS", "HTTP/HTTPS", "Load Balancing", "VPN", "Wi-Fi", "Routing", "Switching", "Network Security",
            "Linux", "Unix", "Windows Server", "Mac OS", "Bash", "PowerShell", "Zsh", "System Administration", "Automation Scripting",
            "Mobile Development", "Android", "iOS", "React Native", "Flutter", "Xamarin", "SwiftUI", "Kotlin Multiplatform", "App Store", "Google Play",
            "Game Development", "Unity", "Unreal Engine", "C#", "Game Design", "3D Modeling", "VR", "AR", "Metaverse", "Gaming APIs"
        ]
        skills = [keyword for keyword in skill_keywords if keyword.lower() in structured_data.lower()]
        return skills

    def extract_experience(self, structured_data: str):
        """Extract experience (in months or years)"""
        match = re.search(r"(\d+)\s*(months|years)", structured_data)
        if match:
            return int(match.group(1))  # Return the numeric value for experience
        return 0  # Default experience if not found