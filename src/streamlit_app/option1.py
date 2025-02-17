# option1.py
from pypdf import PdfReader
import docx
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import google.generativeai as genai
import io
from io import BytesIO
from utils import extract_cv_information, extract_job_posting_information

def customize_resume(cv_file):
    """Placeholder function for AI-powered CV improvement."""

    skills = {
    "Software Development": {
        "Entry-Level": {
            "hard": ["Python", "Java", "Git", "OOP", "HTML", "CSS", "JavaScript", "SQL", "REST APIs", "Debugging", "Unit Testing", "Agile", "SCRUM", "VS Code", "Linux"],
            "soft": ["Teamwork", "Communication", "Problem-Solving", "Attention to Detail", "Time Management", "Adaptability", "Curiosity", "Self-Learning", "Work Ethic", "Collaboration"]
        },
        "Mid-Level": {
            "hard": ["Spring Boot", "Django", "React.js", "Docker", "Microservices", "AWS", "PostgreSQL", "GraphQL", "Kubernetes", "Design Patterns", "Unit Testing", "TDD", "CI/CD", "NoSQL", "Redis"],
            "soft": ["Mentorship", "Critical Thinking", "Decision Making", "Task Prioritization", "Leadership", "Conflict Resolution", "Public Speaking", "Strategic Thinking", "Persuasion", "Agile Thinking"]
        },
        "Senior-Level": {
            "hard": ["System Architecture", "Cloud Computing", "Scalability", "Kubernetes", "CI/CD Pipelines", "Infrastructure as Code", "Security Best Practices", "Performance Optimization", "Distributed Systems", "Message Queues", "Big Data Processing", "Event-Driven Design", "Advanced Algorithms", "Software Design Patterns", "System Integration"],
            "soft": ["Visionary Thinking", "Negotiation", "Technical Leadership", "Stakeholder Communication", "Crisis Management", "Executive Presence", "Cross-Team Collaboration", "Change Management", "Project Roadmap Planning", "Mentorship & Coaching"]
        }
    },
    "Data Science & Machine Learning": {
        "Entry-Level": {
            "hard": ["Python", "Pandas", "NumPy", "Scikit-Learn", "Matplotlib", "Seaborn", "SQL", "Basic Statistics", "Data Cleaning", "Exploratory Data Analysis (EDA)", "Jupyter Notebooks", "Linear Regression", "Classification Models", "Clustering", "Feature Engineering"],
            "soft": ["Attention to Detail", "Logical Thinking", "Problem Solving", "Curiosity", "Self-Learning", "Time Management", "Team Collaboration", "Effective Communication", "Adaptability", "Data Storytelling"]
        },
        "Mid-Level": {
            "hard": ["Machine Learning Pipelines", "Deep Learning (TensorFlow, PyTorch)", "Time Series Analysis", "Model Optimization", "Feature Selection", "Hyperparameter Tuning", "NLP", "MLOps", "Data Visualization (Tableau, Power BI)", "A/B Testing", "Big Data Technologies (Spark, Hadoop)", "Bayesian Statistics", "Recommendation Systems", "Cloud ML Services (AWS/GCP)", "Graph Neural Networks"],
            "soft": ["Decision Making", "Mentorship", "Communication of Insights", "Business Understanding", "Project Management", "Critical Thinking", "Cross-functional Collaboration", "Presentation Skills", "Innovation", "User-Centric Thinking"]
        },
        "Senior-Level": {
            "hard": ["AI Model Deployment", "Production ML Systems", "AutoML", "Advanced Deep Learning Architectures", "Transfer Learning", "Reinforcement Learning", "Graph Theory", "Computer Vision", "Cloud MLOps", "Generative AI", "Multi-Modal Learning", "Model Explainability", "Bias & Fairness in AI", "Data Governance", "High-Performance Computing"],
            "soft": ["Visionary Leadership", "Enterprise Strategy", "AI Ethics & Compliance", "High-Level Decision Making", "Scaling AI Systems", "Thought Leadership", "Risk Management", "Strategic Roadmaps", "Business Model Innovation", "Executive Communication"]
        }
    },
    "Data Engineering": {
        "Entry-Level": {
            "hard": [
                "SQL",
                "Python",
                "ETL Pipelines",
                "Data Cleaning",
                "Data Warehousing",
                "Apache Airflow",
                "Shell Scripting",
                "Git",
                "PostgreSQL",
                "BigQuery",
                "Data Modeling",
                "Pandas",
                "Spark Basics",
                "JSON & XML Parsing",
                "Cloud Storage (AWS S3, GCP Storage)"
            ],
            "soft": [
                "Attention to Detail",
                "Problem-Solving",
                "Time Management",
                "Teamwork",
                "Adaptability",
                "Communication",
                "Self-Learning",
                "Critical Thinking",
                "Documentation Skills",
                "Analytical Thinking"
            ]
        },
        "Mid-Level": {
            "hard": [
                "Advanced SQL Optimization",
                "Data Pipeline Automation",
                "Apache Spark",
                "Kafka",
                "Data Lakes",
                "Redshift",
                "Data Governance",
                "Columnar Storage Formats (Parquet, ORC)",
                "Workflow Orchestration",
                "Containerization (Docker, Kubernetes)",
                "Cloud Data Services (AWS Glue, GCP Dataflow)",
                "Graph Databases",
                "CI/CD for Data Engineering",
                "Data Security & Compliance",
                "Monitoring & Logging (Datadog, Prometheus)"
            ],
            "soft": [
                "Leadership",
                "Mentorship",
                "Cross-Team Collaboration",
                "Project Management",
                "Decision Making",
                "Problem-Solving Under Pressure",
                "Effective Communication",
                "Strategic Thinking",
                "Stakeholder Management",
                "Negotiation Skills"
            ]
        },
        "Senior-Level": {
            "hard": [
                "Data Architecture Design",
                "Real-Time Data Processing",
                "Distributed Systems",
                "Stream Processing (Flink, Spark Streaming)",
                "Machine Learning Data Pipelines",
                "Scalability & Performance Tuning",
                "Cost Optimization in Cloud Data Services",
                "Advanced Data Security & Privacy",
                "Automated Data Lineage & Metadata Management",
                "Graph Processing & Semantic Data Models",
                "Data Monetization Strategies",
                "Infrastructure as Code (Terraform, CloudFormation)",
                "Event-Driven Architecture",
                "Enterprise Data Strategy",
                "Cloud-Native Data Warehousing (BigQuery, Snowflake)"
            ],
            "soft": [
                "Visionary Thinking",
                "Executive Communication",
                "Organizational Leadership",
                "Business-Oriented Decision Making",
                "Crisis Management",
                "Change Management",
                "Long-Term Strategic Planning",
                "Building High-Performance Teams",
                "Negotiation with C-Level Executives",
                "Ethical Data Management & Governance"
            ]
        }
    },
    "Cloud & DevOps": {
        "Entry-Level": {
            "hard": [
                "Linux Basics",
                "Shell Scripting",
                "Git & GitHub",
                "Docker",
                "Basic Networking",
                "Cloud Fundamentals (AWS, GCP, Azure)",
                "CI/CD Basics",
                "Terraform Basics",
                "Monitoring & Logging (CloudWatch, Prometheus)",
                "Bash Scripting",
                "IAM & Access Management",
                "Infrastructure as Code (IaC)",
                "Version Control",
                "Kubernetes Basics",
                "Basic Security Practices"
            ],
            "soft": [
                "Attention to Detail",
                "Problem-Solving",
                "Time Management",
                "Adaptability",
                "Collaboration",
                "Communication Skills",
                "Continuous Learning",
                "Analytical Thinking",
                "Work Ethic",
                "Teamwork"
            ]
        },
        "Mid-Level": {
            "hard": [
                "Advanced CI/CD Pipelines",
                "Configuration Management (Ansible, Puppet, Chef)",
                "Networking & VPNs",
                "Advanced Kubernetes",
                "Serverless Architectures",
                "Cloud Security (IAM, VPC, Security Groups)",
                "Observability & Monitoring (ELK Stack, Grafana)",
                "Multi-Cloud Deployments",
                "Terraform Advanced",
                "Service Mesh (Istio, Linkerd)",
                "API Gateways (Kong, AWS API Gateway)",
                "Chaos Engineering",
                "Cost Optimization Strategies",
                "Cloud Storage & Databases",
                "Automation & Scripting"
            ],
            "soft": [
                "Leadership",
                "Mentorship",
                "Cross-Team Collaboration",
                "Project Management",
                "Decision Making",
                "Effective Communication",
                "Problem Solving Under Pressure",
                "Strategic Thinking",
                "Stakeholder Management",
                "Negotiation Skills"
            ]
        },
        "Senior-Level": {
            "hard": [
                "Cloud Architecture Design",
                "Enterprise DevOps Strategy",
                "Hybrid & Multi-Cloud Management",
                "Advanced Networking & Security",
                "High Availability & Disaster Recovery",
                "Scalability & Performance Optimization",
                "Compliance & Governance (GDPR, SOC 2, HIPAA)",
                "Zero Trust Security Models",
                "Infrastructure as Code Best Practices",
                "AI & ML in DevOps",
                "Advanced Chaos Engineering",
                "Policy as Code (OPA, Sentinel)",
                "Distributed Systems Management",
                "Kubernetes Operators & Custom Controllers",
                "FinOps & Cloud Cost Management"
            ],
            "soft": [
                "Visionary Thinking",
                "Executive Communication",
                "Business-Oriented Decision Making",
                "Crisis Management",
                "Change Management",
                "Long-Term Strategic Planning",
                "Building High-Performance Teams",
                "Cross-Department Coordination",
                "Ethical Leadership",
                "Negotiation with C-Level Executives"
            ]
        }
    
},
    "Cybersecurity": {
        "Entry-Level": {
            "hard": [
                "Networking Basics (TCP/IP, DNS, HTTP)",
                "Linux & Windows Security",
                "Cybersecurity Fundamentals",
                "Firewall Configuration",
                "Basic Cryptography",
                "Penetration Testing Basics",
                "SIEM (Security Information & Event Management)",
                "Endpoint Security",
                "Incident Response Basics",
                "Threat Intelligence Fundamentals",
                "Secure Coding Principles",
                "Risk Assessment Basics",
                "Social Engineering Awareness",
                "Vulnerability Scanning",
                "Compliance & Regulations (GDPR, ISO 27001)"
            ],
            "soft": [
                "Attention to Detail",
                "Problem-Solving",
                "Analytical Thinking",
                "Teamwork",
                "Time Management",
                "Adaptability",
                "Curiosity & Continuous Learning",
                "Communication Skills",
                "Ethical Mindset",
                "Stress Management"
            ]
        },
        "Mid-Level": {
            "hard": [
                "Intrusion Detection Systems (IDS/IPS)",
                "Advanced Penetration Testing",
                "Cloud Security (AWS, Azure, GCP)",
                "Security Information & Event Management (SIEM)",
                "Digital Forensics",
                "Identity & Access Management (IAM)",
                "Zero Trust Architecture",
                "Threat Hunting",
                "Application Security (OWASP, Secure SDLC)",
                "Malware Analysis",
                "Red Teaming & Blue Teaming",
                "Network Traffic Analysis",
                "Incident Response & Forensics",
                "Security Automation & Scripting (Python, Bash)",
                "Compliance & Governance (NIST, HIPAA, PCI-DSS)"
            ],
            "soft": [
                "Leadership",
                "Mentorship",
                "Cross-Team Collaboration",
                "Decision Making",
                "Project Management",
                "Effective Communication",
                "Critical Thinking",
                "Strategic Planning",
                "Risk Assessment & Mitigation",
                "Stakeholder Engagement"
            ]
        },
        "Senior-Level": {
            "hard": [
                "Cybersecurity Strategy & Architecture",
                "Enterprise Risk Management",
                "Advanced Threat Intelligence",
                "Security Operations Center (SOC) Management",
                "Cloud-Native Security",
                "DevSecOps Integration",
                "Blockchain Security",
                "Zero-Day Exploit Analysis",
                "Security Policy & Compliance Enforcement",
                "Artificial Intelligence in Cybersecurity",
                "Advanced Data Encryption & Key Management",
                "Incident Response & Crisis Management",
                "Cybersecurity Budgeting & Resource Allocation",
                "Cyber Warfare & Nation-State Threats",
                "Legal & Regulatory Compliance at Scale"
            ],
            "soft": [
                "Visionary Thinking",
                "Executive Communication",
                "Business-Oriented Decision Making",
                "Crisis Management",
                "Change Management",
                "Long-Term Strategic Planning",
                "Building & Leading High-Performance Teams",
                "Ethical Leadership",
                "Negotiation with C-Level Executives",
                "Public Speaking & Thought Leadership"
            ]
        }
    },
    "Business Intelligence & Data Analytics": {
        "Entry-Level": {
            "hard": [
                "SQL",
                "Excel & Google Sheets",
                "Data Visualization (Tableau, Power BI)",
                "Basic Statistics",
                "Data Cleaning",
                "ETL Processes",
                "Google Analytics",
                "Business Reporting",
                "Python for Data Analysis",
                "Dashboards Creation",
                "Data Governance Basics",
                "A/B Testing Fundamentals",
                "KPI Definition & Monitoring",
                "Data Warehousing Concepts",
                "Data Storytelling"
            ],
            "soft": [
                "Attention to Detail",
                "Problem-Solving",
                "Critical Thinking",
                "Time Management",
                "Adaptability",
                "Communication Skills",
                "Teamwork",
                "Curiosity & Continuous Learning",
                "Stakeholder Engagement",
                "Presentation Skills"
            ]
        },
        "Mid-Level": {
            "hard": [
                "Advanced SQL & Query Optimization",
                "Data Modeling & Warehousing",
                "Predictive Analytics",
                "Big Data Tools (Spark, Hadoop)",
                "Advanced Data Visualization",
                "Cloud Data Platforms (AWS Redshift, GCP BigQuery, Snowflake)",
                "Data Pipeline Automation",
                "Machine Learning for Analytics",
                "Financial & Operational Metrics Analysis",
                "Customer Segmentation",
                "ETL Tools (Informatica, Talend, dbt)",
                "Data Quality Management",
                "Advanced KPI Design",
                "Business Process Optimization",
                "Statistical Forecasting"
            ],
            "soft": [
                "Leadership",
                "Mentorship",
                "Decision Making",
                "Effective Communication",
                "Cross-Team Collaboration",
                "Strategic Thinking",
                "Project Management",
                "Stakeholder Management",
                "Problem-Solving Under Pressure",
                "Negotiation Skills"
            ]
        },
        "Senior-Level": {
            "hard": [
                "Enterprise Data Strategy",
                "Executive Dashboards & Reporting",
                "Cloud Data Architecture",
                "Advanced Data Governance",
                "AI & ML Integration in BI",
                "Data-Driven Business Decision Making",
                "Real-Time Analytics",
                "Market & Competitive Intelligence",
                "Large-Scale Data Engineering for BI",
                "Embedded Analytics",
                "Regulatory & Compliance Reporting",
                "Performance Optimization Strategies",
                "Multi-Cloud Data Management",
                "Data Monetization Strategies",
                "Digital Transformation Leadership"
            ],
            "soft": [
                "Visionary Thinking",
                "Executive Communication",
                "Business-Oriented Decision Making",
                "Crisis Management",
                "Change Management",
                "Long-Term Strategic Planning",
                "Ethical Leadership",
                "Building & Leading High-Performance Teams",
                "Negotiation with C-Level Executives",
                "Public Speaking & Thought Leadership"
            ]
        }
    },
    "IT Support & SysAdmin": {
        "Entry-Level": {
            "hard": [
                "Windows & Linux Administration",
                "Networking Basics (TCP/IP, DNS, DHCP)",
                "Active Directory Management",
                "Basic Troubleshooting",
                "Help Desk & Ticketing Systems (Jira, ServiceNow)",
                "Hardware & Software Support",
                "Remote Desktop Tools (TeamViewer, AnyDesk)",
                "Scripting Basics (PowerShell, Bash)",
                "System Monitoring (Nagios, Zabbix)",
                "Cybersecurity Fundamentals",
                "User Account Management",
                "Cloud Basics (AWS, Azure, GCP)",
                "ITIL Foundations",
                "Backup & Recovery Strategies",
                "Printer & Peripheral Support"
            ],
            "soft": [
                "Problem-Solving",
                "Customer Service",
                "Patience",
                "Communication Skills",
                "Time Management",
                "Attention to Detail",
                "Adaptability",
                "Teamwork",
                "Multitasking",
                "Stress Management"
            ]
        },
        "Mid-Level": {
            "hard": [
                "Advanced Networking (VLANs, VPN, Firewall Management)",
                "Windows Server & Linux Server Administration",
                "Virtualization (VMware, Hyper-V)",
                "Cloud Infrastructure Management",
                "Configuration Management (Ansible, Puppet, Chef)",
                "Cybersecurity Best Practices",
                "Disaster Recovery Planning",
                "Advanced Troubleshooting",
                "Log Analysis & System Auditing",
                "Automated Scripting (PowerShell, Python, Bash)",
                "IT Compliance & Governance (ISO 27001, GDPR)",
                "Patch Management",
                "Database Administration (MySQL, PostgreSQL, MSSQL)",
                "Identity & Access Management (IAM)",
                "Containerization (Docker, Kubernetes)"
            ],
            "soft": [
                "Leadership",
                "Mentorship",
                "Effective Communication",
                "Decision Making",
                "Cross-Team Collaboration",
                "Incident Management",
                "Strategic Thinking",
                "Conflict Resolution",
                "Customer Relationship Management",
                "Problem-Solving Under Pressure"
            ]
        },
        "Senior-Level": {
            "hard": [
                "Enterprise IT Architecture",
                "Cloud & Hybrid Infrastructure Design",
                "Advanced Security & Threat Management",
                "High Availability & Failover Strategies",
                "Network Automation & Orchestration",
                "DevOps & CI/CD Integration",
                "Capacity Planning & Performance Optimization",
                "Compliance & Risk Management",
                "Disaster Recovery & Business Continuity",
                "Enterprise-Level Virtualization & Container Management",
                "IT Budgeting & Cost Optimization",
                "Zero Trust Security Architecture",
                "Infrastructure as Code (Terraform, CloudFormation)",
                "SIEM & Threat Intelligence",
                "Advanced System Hardening Techniques"
            ],
            "soft": [
                "Visionary Thinking",
                "Executive Communication",
                "Strategic Planning",
                "Crisis Management",
                "Change Management",
                "Ethical Leadership",
                "Building & Leading High-Performance Teams",
                "Negotiation with C-Level Executives",
                "Long-Term IT Roadmap Planning",
                "Public Speaking & Thought Leadership"
            ]
        }
    },
    "Product Management & Agile Roles": {
        "Entry-Level": {
            "hard": [
                "Agile Methodologies (Scrum, Kanban)",
                "Product Lifecycle Management",
                "Market Research & Analysis",
                "User Story Writing",
                "Wireframing & Prototyping (Figma, Balsamiq)",
                "Basic UX/UI Principles",
                "Data Analysis & A/B Testing",
                "Google Analytics & Product Metrics",
                "JIRA & Confluence",
                "Stakeholder Communication",
                "Competitive Analysis",
                "Prioritization Techniques (MoSCoW, RICE)",
                "Roadmap Planning Basics",
                "Customer Feedback Collection & Analysis",
                "Lean Startup & MVP Development"
            ],
            "soft": [
                "Adaptability",
                "Critical Thinking",
                "Problem-Solving",
                "Collaboration",
                "Communication Skills",
                "Time Management",
                "Curiosity & Continuous Learning",
                "Empathy",
                "Negotiation Basics",
                "Attention to Detail"
            ]
        },
        "Mid-Level": {
            "hard": [
                "Advanced Product Strategy",
                "OKRs & KPI Definition",
                "Customer Journey Mapping",
                "Design Thinking",
                "Go-to-Market Strategy",
                "Revenue & Business Model Analysis",
                "Advanced Data Analytics (SQL, Python for PMs)",
                "Experimentation Frameworks",
                "Growth Hacking Strategies",
                "SaaS & Subscription Business Models",
                "Cross-functional Team Management",
                "Agile Coaching",
                "Competitive Benchmarking",
                "Stakeholder Management",
                "Storytelling with Data"
            ],
            "soft": [
                "Leadership",
                "Decision Making",
                "Mentorship",
                "Effective Communication",
                "Conflict Resolution",
                "Negotiation with Stakeholders",
                "Strategic Thinking",
                "Cross-Team Collaboration",
                "Risk Management",
                "Customer-Centric Mindset"
            ]
        },
        "Senior-Level": {
            "hard": [
                "Enterprise Product Strategy & Vision",
                "Scaling Agile Frameworks (SAFe, LeSS)",
                "Mergers & Acquisitions Strategy",
                "C-Level Stakeholder Management",
                "International Market Expansion",
                "Behavioral Economics in Product Design",
                "Advanced Pricing Strategies",
                "Regulatory Compliance & Legal Considerations",
                "Portfolio Management",
                "AI & Data-Driven Decision Making",
                "Investment & Venture Capital Analysis",
                "Change Management in Product Development",
                "Ecosystem & Platform Thinking",
                "Advanced UX Research & Psychology",
                "Digital Transformation Strategy"
            ],
            "soft": [
                "Visionary Leadership",
                "Executive Communication",
                "Enterprise-Wide Decision Making",
                "Crisis Management",
                "Scaling & Structuring Product Teams",
                "Long-Term Strategic Planning",
                "Public Speaking & Thought Leadership",
                "Ethical Leadership",
                "Stakeholder & Investor Relations",
                "Cultural & Organizational Change Management"
            ]
        }
    },
    "AI Research & NLP": {
        "Entry-Level": {
            "hard": [
                "Python",
                "Machine Learning Fundamentals",
                "Deep Learning Basics",
                "Natural Language Processing (NLP) Basics",
                "Text Preprocessing Techniques",
                "Sentiment Analysis",
                "Named Entity Recognition (NER)",
                "Word Embeddings (Word2Vec, GloVe, FastText)",
                "TensorFlow & PyTorch Basics",
                "Speech Recognition Fundamentals",
                "Transformer Models (BERT, GPT Basics)",
                "Reinforcement Learning Basics",
                "Data Collection & Cleaning",
                "Basic Statistical NLP Techniques",
                "Hugging Face Library"
            ],
            "soft": [
                "Analytical Thinking",
                "Problem-Solving",
                "Curiosity & Continuous Learning",
                "Attention to Detail",
                "Collaboration & Teamwork",
                "Communication Skills",
                "Time Management",
                "Adaptability",
                "Critical Thinking",
                "Data Storytelling"
            ]
        },
        "Mid-Level": {
            "hard": [
                "Advanced Deep Learning Architectures",
                "Transformers & Attention Mechanisms",
                "Transfer Learning",
                "Fine-Tuning Pretrained Models",
                "Generative Models (GANs, VAEs)",
                "Recurrent Neural Networks (RNNs, LSTMs, GRUs)",
                "Multi-Modal Learning",
                "Speech-to-Text & Text-to-Speech Models",
                "Zero-Shot & Few-Shot Learning",
                "Ethical AI & Bias Mitigation",
                "Reinforcement Learning for NLP",
                "Federated Learning in NLP",
                "Big Data Processing (Spark NLP, Dask)",
                "Graph Neural Networks for NLP",
                "Low-Resource Language Modeling"
            ],
            "soft": [
                "Leadership",
                "Decision Making",
                "Mentorship & Coaching",
                "Cross-Team Collaboration",
                "Project Management",
                "Effective Communication",
                "Strategic Thinking",
                "Negotiation Skills",
                "Stakeholder Engagement",
                "Innovative Thinking"
            ]
        },
        "Senior-Level": {
            "hard": [
                "AI Model Deployment at Scale",
                "Optimization of Large-Scale NLP Models",
                "Knowledge Graphs & Ontologies",
                "Explainable AI (XAI) in NLP",
                "Conversational AI & Chatbots",
                "Multilingual NLP & Cross-Language Transfer",
                "Neural Machine Translation (NMT)",
                "Large-Scale Information Retrieval Systems",
                "AI Ethics & Governance",
                "Advanced Probabilistic Models for NLP",
                "Self-Supervised & Unsupervised NLP Techniques",
                "AI Research Paper Writing & Review",
                "Domain-Specific NLP Applications",
                "AI-Powered Search Engines",
                "AI for Healthcare & Biomedical NLP"
            ],
            "soft": [
                "Visionary Thinking",
                "Executive Communication",
                "Crisis Management",
                "Enterprise-Wide AI Strategy",
                "Building & Leading Research Teams",
                "Industry & Academia Collaboration",
                "AI Policy & Ethics Advocacy",
                "Long-Term AI Roadmap Planning",
                "C-Level Stakeholder Engagement",
                "Public Speaking & Thought Leadership"
            ]
        }
    },
    "Blockchain & Web3": {
        "Entry-Level": {
            "hard": [
                "Blockchain Fundamentals",
                "Ethereum & Smart Contracts",
                "Solidity Programming",
                "Bitcoin & Cryptography Basics",
                "Decentralized Applications (dApps)",
                "Web3.js & Ethers.js",
                "Consensus Mechanisms (PoW, PoS, DPoS)",
                "Token Standards (ERC-20, ERC-721, ERC-1155)",
                "Basic Cybersecurity for Blockchain",
                "NFT Development",
                "Wallets & Key Management",
                "IPFS & Decentralized Storage",
                "Metamask & Wallet Integration",
                "DeFi Protocols Basics",
                "Gas Optimization Techniques"
            ],
            "soft": [
                "Problem-Solving",
                "Analytical Thinking",
                "Curiosity & Continuous Learning",
                "Attention to Detail",
                "Collaboration & Teamwork",
                "Communication Skills",
                "Time Management",
                "Adaptability",
                "Critical Thinking",
                "Entrepreneurial Mindset"
            ]
        },
        "Mid-Level": {
            "hard": [
                "Advanced Smart Contract Development",
                "Layer 2 Scaling Solutions (Optimistic & ZK Rollups)",
                "Cross-Chain Interoperability",
                "Advanced Cryptographic Algorithms",
                "Oracles & Data Feeds",
                "Automated Market Makers (AMMs)",
                "Blockchain Governance Models",
                "Advanced DeFi Protocols",
                "DAO Development & Governance",
                "Decentralized Identity Management",
                "Security Audits for Smart Contracts",
                "Optimizing Gas Fees in Smart Contracts",
                "Bridges & Sidechains",
                "Privacy-Preserving Techniques (ZK-SNARKs, ZK-STARKs)",
                "Regulatory & Compliance Considerations"
            ],
            "soft": [
                "Leadership",
                "Decision Making",
                "Mentorship & Coaching",
                "Cross-Team Collaboration",
                "Project Management",
                "Effective Communication",
                "Strategic Thinking",
                "Negotiation Skills",
                "Stakeholder Engagement",
                "Innovative Thinking"
            ]
        },
        "Senior-Level": {
            "hard": [
                "Enterprise Blockchain Solutions",
                "Consensus Algorithm Design & Optimization",
                "Advanced Tokenomics & Economic Modeling",
                "Blockchain Scalability & Performance Engineering",
                "Regulatory Frameworks for Blockchain",
                "Security Architecture for Web3",
                "AI & Blockchain Integration",
                "Quantum-Resistant Cryptography",
                "Decentralized Finance (DeFi) Risk Analysis",
                "Zero-Knowledge Proofs & Privacy Enhancements",
                "Multi-Chain Strategies & Interoperability",
                "Blockchain Governance & Policy Making",
                "Institutional Adoption of Blockchain",
                "Sustainable Blockchain Solutions",
                "Tokenized Assets & Securities"
            ],
            "soft": [
                "Visionary Thinking",
                "Executive Communication",
                "Crisis Management",
                "Enterprise-Wide Blockchain Strategy",
                "Building & Leading Research Teams",
                "Industry & Academia Collaboration",
                "Blockchain Policy & Ethics Advocacy",
                "Long-Term Web3 Roadmap Planning",
                "C-Level Stakeholder Engagement",
                "Public Speaking & Thought Leadership"
            ]
        }
    },
    "Embedded Systems & IoT": {
        "Entry-Level": {
            "hard": [
                "C/C++ Programming",
                "Microcontroller Programming (Arduino, ESP32, STM32)",
                "Embedded Linux Basics",
                "Real-Time Operating Systems (RTOS)",
                "GPIO & Peripheral Interfaces (SPI, I2C, UART)",
                "Sensors & Actuators",
                "Basic PCB Design & Soldering",
                "IoT Communication Protocols (MQTT, CoAP, HTTP)",
                "Firmware Debugging Tools (JTAG, SWD)",
                "Wireless Technologies (Wi-Fi, Bluetooth, LoRa, Zigbee)",
                "Embedded Software Development",
                "Memory Management in Embedded Systems",
                "Basic Signal Processing",
                "Low-Power Design Techniques",
                "Basic Cybersecurity for IoT"
            ],
            "soft": [
                "Problem-Solving",
                "Attention to Detail",
                "Curiosity & Continuous Learning",
                "Team Collaboration",
                "Analytical Thinking",
                "Communication Skills",
                "Time Management",
                "Adaptability",
                "Critical Thinking",
                "Hands-on Prototyping Skills"
            ]
        },
        "Mid-Level": {
            "hard": [
                "Advanced Embedded C/C++",
                "Linux Device Drivers",
                "Real-Time Systems Design",
                "IoT Edge Computing",
                "Cloud IoT Platforms (AWS IoT, Azure IoT, Google Cloud IoT)",
                "Advanced PCB Design & Prototyping",
                "FPGA Programming",
                "Machine Learning for Edge Devices",
                "Advanced Power Management",
                "Secure Boot & Firmware Updates",
                "Wireless Protocol Optimization",
                "AIoT (AI-powered IoT)",
                "Interfacing with Industrial IoT (IIoT)",
                "Embedded System Virtualization",
                "Automated Testing for Embedded Software"
            ],
            "soft": [
                "Leadership",
                "Decision Making",
                "Mentorship & Coaching",
                "Cross-Team Collaboration",
                "Project Management",
                "Effective Communication",
                "Strategic Thinking",
                "Innovation Management",
                "Stakeholder Engagement",
                "Problem-Solving Under Pressure"
            ]
        },
        "Senior-Level": {
            "hard": [
                "System-on-Chip (SoC) Design & Development",
                "Edge AI & Federated Learning",
                "High-Performance Embedded Computing (HPEC)",
                "Advanced Industrial IoT Architectures",
                "5G & Next-Gen Wireless Communication for IoT",
                "Cyber-Physical Systems Security",
                "Blockchain for IoT Security",
                "Automotive Embedded Systems (ISO 26262, AUTOSAR)",
                "Medical Embedded Systems & Compliance (IEC 62304)",
                "Energy-Efficient Computing Architectures",
                "IoT Governance & Data Privacy Regulations",
                "Neuromorphic Computing for Embedded Systems",
                "Heterogeneous Computing (CPU, GPU, FPGA, ASIC)",
                "Standardization & Compliance in Embedded Systems",
                "IoT Sustainability & Green Technology"
            ],
            "soft": [
                "Visionary Thinking",
                "Executive Communication",
                "Enterprise-Wide IoT Strategy",
                "Crisis Management",
                "Long-Term Strategic Planning",
                "Building & Leading High-Performance Teams",
                "Negotiation with C-Level Executives",
                "Ethical Leadership in IoT",
                "Public Speaking & Thought Leadership",
                "Industry & Academia Collaboration"
            ]
        }
    },
    "Game Development": {
        "Entry-Level": {
            "hard": [
                "C# & Unity Development",
                "C++ & Unreal Engine Basics",
                "2D & 3D Game Physics",
                "Game AI Fundamentals",
                "Basic Game UI/UX Design",
                "Game Asset Integration",
                "Animation & Rigging Basics",
                "Shader Programming (HLSL, GLSL)",
                "Scripting for Gameplay Mechanics",
                "Basic Networking for Multiplayer Games",
                "Mobile Game Development (Android, iOS)",
                "Game Audio Implementation",
                "Basic Game Testing & Debugging",
                "Level Design Fundamentals",
                "Version Control (Git, Perforce)"
            ],
            "soft": [
                "Creativity",
                "Problem-Solving",
                "Attention to Detail",
                "Team Collaboration",
                "Communication Skills",
                "Time Management",
                "Adaptability",
                "Passion for Gaming",
                "Critical Thinking",
                "Continuous Learning"
            ]
        },
        "Mid-Level": {
            "hard": [
                "Advanced C++ & Unreal Engine Development",
                "Game Engine Optimization",
                "Procedural Content Generation",
                "Advanced Physics Simulations",
                "AI Pathfinding & Behavior Trees",
                "Multiplayer Networking (Photon, Mirror, Netcode)",
                "Game Analytics & Player Behavior Tracking",
                "Virtual Reality (VR) & Augmented Reality (AR)",
                "Rendering Optimization Techniques",
                "Advanced UI/UX for Games",
                "Advanced Game Testing & Automation",
                "Live Ops & Game Monetization Strategies",
                "Mobile Game Optimization",
                "Post-Processing & Visual Effects",
                "Cloud-Based Game Development"
            ],
            "soft": [
                "Leadership",
                "Mentorship & Coaching",
                "Strategic Thinking",
                "Project Management",
                "Effective Communication",
                "Cross-Department Collaboration",
                "Problem-Solving Under Pressure",
                "Negotiation Skills",
                "Stakeholder Engagement",
                "Innovation & Creativity"
            ]
        },
        "Senior-Level": {
            "hard": [
                "Game Engine Architecture",
                "High-Performance Rendering & Graphics Programming",
                "Procedural World Generation",
                "Advanced AI & Machine Learning for Games",
                "Scalability in Online Multiplayer Games",
                "Blockchain Integration in Gaming",
                "Game Economy Design & Balancing",
                "Esports & Competitive Gaming Infrastructure",
                "Game Streaming & Cloud Gaming Technologies",
                "Cross-Platform Game Development",
                "Advanced Audio Engineering for Games",
                "Metaverse Development",
                "Cinematic & Storytelling Techniques in Games",
                "Advanced Game Security & Anti-Cheat Systems",
                "Publishing & Distribution Strategies"
            ],
            "soft": [
                "Visionary Thinking",
                "Executive Communication",
                "Industry Leadership & Trend Analysis",
                "Crisis Management",
                "Long-Term Strategic Planning",
                "Ethical Leadership in Gaming",
                "Negotiation with Publishers & Investors",
                "Building & Leading High-Performance Teams",
                "Public Speaking & Thought Leadership",
                "Cultural & Market Adaptation in Game Development"
            ]
        }
    },
    "Networking & Telecommunications": {
        "Entry-Level": {
            "hard": [
                "TCP/IP Fundamentals",
                "OSI Model",
                "Basic Network Configuration",
                "Subnetting & IP Addressing",
                "Routing & Switching Basics",
                "LAN & WAN Technologies",
                "Wireless Networking (Wi-Fi, Bluetooth)",
                "Network Security Basics (Firewalls, VPNs)",
                "DNS & DHCP Configuration",
                "Command-Line Network Tools (Ping, Traceroute, Netstat)",
                "VoIP Fundamentals",
                "Cloud Networking Basics",
                "Network Monitoring Tools (Wireshark, SNMP)",
                "Basic Linux Networking",
                "Ethernet & Cabling Standards"
            ],
            "soft": [
                "Problem-Solving",
                "Attention to Detail",
                "Analytical Thinking",
                "Time Management",
                "Communication Skills",
                "Teamwork",
                "Adaptability",
                "Continuous Learning",
                "Customer Service Skills",
                "Technical Documentation"
            ]
        },
        "Mid-Level": {
            "hard": [
                "Advanced Routing Protocols (BGP, OSPF, EIGRP)",
                "Network Automation & Scripting (Python, Ansible)",
                "SDN (Software-Defined Networking)",
                "Cloud Networking (AWS, Azure, GCP)",
                "QoS (Quality of Service) Implementation",
                "Network Virtualization (VLAN, VXLAN, VRF)",
                "Wireless Network Optimization",
                "Cybersecurity Best Practices in Networking",
                "VoIP & Unified Communications",
                "Load Balancing & Traffic Shaping",
                "Network Performance Tuning",
                "IPv6 Deployment & Migration",
                "Advanced Firewall Configurations",
                "Zero Trust Security Models",
                "Network Redundancy & High Availability"
            ],
            "soft": [
                "Leadership",
                "Project Management",
                "Cross-Team Collaboration",
                "Critical Thinking",
                "Effective Communication",
                "Risk Management",
                "Decision Making",
                "Mentorship & Coaching",
                "Incident Response & Crisis Handling",
                "Vendor & Supplier Management"
            ]
        },
        "Senior-Level": {
            "hard": [
                "Enterprise Network Architecture",
                "5G & Next-Gen Wireless Technologies",
                "IoT Networking & Edge Computing",
                "Cloud-Native Networking",
                "Cybersecurity Strategy for Networks",
                "Data Center Networking",
                "Advanced Network Forensics & Threat Intelligence",
                "Satellite & Optical Communications",
                "Carrier-Grade Network Engineering",
                "Network Infrastructure as Code",
                "Hybrid Cloud & Multi-Cloud Networking",
                "Compliance & Regulatory Standards (ISO, NIST, GDPR)",
                "Advanced Network Performance Engineering",
                "AI & Machine Learning for Network Optimization",
                "Business Continuity & Disaster Recovery Planning"
            ],
            "soft": [
                "Visionary Thinking",
                "Strategic Planning",
                "Enterprise-Level Decision Making",
                "Executive Communication",
                "Crisis Management",
                "Change Management",
                "Building & Leading High-Performance Teams",
                "Industry Thought Leadership",
                "Ethical Leadership in Networking",
                "Negotiation with C-Level Executives & Regulators"
            ]
        }
    },
    "Quality Assurance (QA) & Testing": {
        "Entry-Level": {
            "hard": [
                "Manual Testing Fundamentals",
                "Test Case Design & Execution",
                "Bug Tracking & Reporting (JIRA, Bugzilla)",
                "Basic SQL for Data Validation",
                "Functional & Non-Functional Testing",
                "Regression Testing",
                "Exploratory Testing",
                "Mobile App Testing Basics",
                "API Testing with Postman",
                "Version Control (Git Basics)",
                "Agile & Scrum Methodologies",
                "Test Plan Documentation",
                "Cross-Browser Testing",
                "Basic Automation Testing (Selenium, Cypress)",
                "Understanding Software Development Life Cycle (SDLC)"
            ],
            "soft": [
                "Attention to Detail",
                "Problem-Solving",
                "Analytical Thinking",
                "Communication Skills",
                "Time Management",
                "Teamwork",
                "Adaptability",
                "Curiosity & Continuous Learning",
                "Critical Thinking",
                "Collaboration with Developers"
            ]
        },
        "Mid-Level": {
            "hard": [
                "Test Automation Frameworks (Selenium, Cypress, Appium)",
                "Performance Testing (JMeter, LoadRunner)",
                "Security Testing Basics",
                "CI/CD Integration for Testing",
                "Advanced API Testing (REST Assured, SoapUI)",
                "BDD & TDD Methodologies",
                "Database Testing (SQL, NoSQL)",
                "Containerized Testing (Docker, Kubernetes)",
                "Code Coverage & Static Analysis Tools (SonarQube)",
                "Test Data Management Strategies",
                "Accessibility Testing (WCAG, Axe)",
                "Advanced Mobile Testing (Espresso, XCTest)",
                "Cloud-Based Testing (SauceLabs, BrowserStack)",
                "AI & Machine Learning in Testing",
                "Risk-Based Testing Approaches"
            ],
            "soft": [
                "Leadership",
                "Project Management",
                "Decision Making",
                "Effective Communication",
                "Critical Thinking",
                "Mentorship & Coaching",
                "Cross-Team Collaboration",
                "Strategic Thinking",
                "Stakeholder Engagement",
                "Problem-Solving Under Pressure"
            ]
        },
        "Senior-Level": {
            "hard": [
                "Test Strategy & Enterprise QA Planning",
                "DevOps & Continuous Testing",
                "AI-Powered Test Automation",
                "Advanced Security Testing",
                "Enterprise Performance & Load Testing",
                "Compliance & Regulatory Testing (GDPR, HIPAA, ISO)",
                "Advanced CI/CD Pipelines with Automated Testing",
                "Scalability & High Availability Testing",
                "Penetration Testing & Ethical Hacking",
                "AI-Based Defect Prediction",
                "Shift-Left & Shift-Right Testing Strategies",
                "Cloud-Native Application Testing",
                "Blockchain Application Testing",
                "End-to-End Business Process Testing",
                "QA Governance & Quality Metrics"
            ],
            "soft": [
                "Visionary Thinking",
                "Executive Communication",
                "Enterprise-Wide QA Strategy",
                "Crisis Management",
                "Change Management",
                "Building & Leading High-Performance Teams",
                "Ethical Leadership in QA",
                "Industry Thought Leadership",
                "Negotiation with C-Level Executives",
                "Public Speaking & Advocacy for Quality Culture"
            ]
        }
    },
    "IT Sales & Pre-Sales": {
        "Entry-Level": {
            "hard": [
                "Basic IT & Software Knowledge",
                "CRM Software (Salesforce, HubSpot)",
                "Lead Generation Techniques",
                "Cold Calling & Email Prospecting",
                "Presentation & Demonstration Skills",
                "Sales Funnel Management",
                "Understanding Customer Needs & Requirements",
                "Basic Cloud Computing Concepts",
                "Competitor & Market Analysis",
                "Technical Product Knowledge",
                "Negotiation Basics",
                "Proposal Writing",
                "Basic Contract & SLA Understanding",
                "Customer Relationship Management",
                "Social Selling & LinkedIn Outreach"
            ],
            "soft": [
                "Communication Skills",
                "Persuasion & Influence",
                "Active Listening",
                "Adaptability",
                "Resilience & Persistence",
                "Time Management",
                "Collaboration & Teamwork",
                "Problem-Solving",
                "Empathy",
                "Confidence"
            ]
        },
        "Mid-Level": {
            "hard": [
                "Advanced Sales Strategies",
                "Solution Selling & Consultative Sales",
                "Customer Pain Point Analysis",
                "Cloud & SaaS Solutions Sales",
                "Technical Demonstrations & Proof of Concept (PoC)",
                "Bid & RFP Response Management",
                "Sales Pipeline Forecasting",
                "Cybersecurity & Compliance Knowledge",
                "Competitive Positioning & Value Selling",
                "Account-Based Marketing (ABM)",
                "Multi-Channel Sales Strategies",
                "Data-Driven Sales Analytics",
                "Building & Managing Partner Networks",
                "Contract & SLA Negotiation",
                "Enterprise IT Sales Strategies"
            ],
            "soft": [
                "Strategic Thinking",
                "Leadership & Team Management",
                "Negotiation & Deal Closing",
                "Stakeholder Management",
                "Conflict Resolution",
                "Effective Communication with C-Level Executives",
                "Decision Making Under Pressure",
                "Cross-Team Collaboration",
                "Client Relationship Building",
                "Innovation & Business Development"
            ]
        },
        "Senior-Level": {
            "hard": [
                "Enterprise-Level IT Sales Strategy",
                "Building & Scaling Sales Teams",
                "High-Value Contract Negotiation",
                "Global Sales & Market Expansion",
                "Mergers & Acquisitions in IT Sales",
                "Advanced Competitive Analysis & Market Intelligence",
                "ROI-Based Selling & Financial Justification",
                "Customer Success & Retention Strategies",
                "Legal & Compliance Knowledge for IT Sales",
                "Pricing Strategy & Revenue Optimization",
                "AI & Data-Driven Sales Forecasting",
                "Multi-Cloud & Hybrid IT Solution Sales",
                "Government & Enterprise Bidding Strategies",
                "Digital Transformation Consulting",
                "Strategic Partnership Development"
            ],
            "soft": [
                "Visionary Leadership",
                "Executive-Level Negotiation",
                "Public Speaking & Thought Leadership",
                "Crisis Management",
                "Long-Term Strategic Planning",
                "High-Stakes Decision Making",
                "Building & Managing High-Performance Sales Teams",
                "C-Level Relationship Management",
                "Ethical Sales Leadership",
                "Industry Influence & Market Shaping"
            ]
        }
    }
}

    

    print(skills.keys())



def run():
    uploaded_cv = st.file_uploader("Upload your PDF resume", type=["pdf"])
    job_selection_method = st.radio("How would you like to provide the job details?", ["Option 1: Upload a job description", "Option 2: Select from our job database"])
    
    if job_selection_method == "Option 1: Upload a job description":
        uploaded_job = st.file_uploader("Upload your PDF Job Description", type=["pdf"])

    else:
        jobs = pd.DataFrame(list(collection.find({}, {"_id": 0, "Title": 1, "Location": 1})))
        selected_job = st.selectbox("Choose a job from our database:", jobs["Title"]) 
        uploaded_job = collection.find_one({"Title": selected_job})
    
    if ((uploaded_cv is not None) and (uploaded_job is not None)):
        
        extract_cv_information(uploaded_cv)
        extract_job_posting_information(uploaded_job)
        customize_resume(uploaded_cv)
        # st.download_button("Download Tailored Resume", customized_cv, file_name="Tailored_Resume.pdf")