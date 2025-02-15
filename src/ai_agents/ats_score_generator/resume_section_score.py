import spacy
from pdfminer.high_level import extract_text
from sentence_transformers import SentenceTransformer, util

# Load the English NLP model and Sentence Transformer for semantic matching
nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("all-mpnet-base-v2")  # More accurate semantic model

# Standard ATS-Compatible Section Titles
VALID_SECTIONS = [
    "Work Experience", "Education", "Skills", "Certifications", "Summary"
]

def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    return extract_text(pdf_path)
    
def check_resume_sections(resume_text):
    """
    Validate that the resume contains ATS-friendly section headers using NLP-based semantic matching.
    Returns a completeness score (0-100%) based on section presence.
    """
    detected_sections = set()
    
    for line in resume_text.split("\n"):
        line = line.strip()
        if line:
            section_embedding = model.encode(line, convert_to_tensor=True)
            valid_embeddings = model.encode(VALID_SECTIONS, convert_to_tensor=True)
            similarity_scores = util.pytorch_cos_sim(section_embedding, valid_embeddings)
            best_match_idx = similarity_scores.argmax().item()
            best_match_score = similarity_scores[0][best_match_idx].item()
            
            if best_match_score > 0.80:
                detected_sections.add(VALID_SECTIONS[best_match_idx])
    
    missing_sections = [s for s in VALID_SECTIONS if s not in detected_sections]
    section_score = round((len(detected_sections) / len(VALID_SECTIONS)) * 100, 2)
    
    return {"detected_sections": list(detected_sections), "missing_sections": missing_sections, "section_score": section_score}

def extract_and_check_resume_sections(pdf_path):
    """
    Extracts text from a given PDF file and checks for ATS-friendly section headers.
    """
    resume_text = extract_text_from_pdf(pdf_path)
    return check_resume_sections(resume_text)

if __name__ == "__main__":
    pdf_path = "src/resumes/resume_sample_4.pdf"
    section_check = extract_and_check_resume_sections(pdf_path)
    print("Sections Found:", section_check["detected_sections"])
    print("Missing Sections:", section_check["missing_sections"])
    print(f"Section Completeness Score: {section_check['section_score']}%")

# Reference
# (OpenAI first prompt, 2025): How can we use NLP to check for valid resume sections?
# (OpenAI last prompt, 2025):  Can you show an example of checking for valid resume sections using NLP?