import os
import pdfplumber
from resume_format_score import check_resume_format
from resume_section_score import extract_and_check_resume_sections
from resume_action_verb_score import identify_action_verbs, rank_action_verbs

def extract_text_from_pdf(pdf_path):
    """Extracts text from the given PDF file using pdfplumber."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Error: The file '{pdf_path}' was not found. Check the path.")
    
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() + '\n'
    return text

def calculate_ats_score(pdf_path):
    """Calculates the final ATS score by aggregating all scoring components."""
    resume_text = extract_text_from_pdf(pdf_path)
    
    # Run individual ATS checks
    format_result = check_resume_format(pdf_path)
    format_score = format_result.get("format_score", 0)
    
    section_result = extract_and_check_resume_sections(pdf_path)
    section_score = section_result.get("section_score", 0)
    detected_sections = section_result.get("detected_sections", [])
    missing_sections = section_result.get("missing_sections", [])
    
    verbs = identify_action_verbs(resume_text)
    ranked_verbs, action_score, top_verbs = rank_action_verbs(verbs)
    
    # Final ATS Score Calculation
    ats_score = (
        0.50 * format_score +
        0.25 * section_score +
        0.25 * action_score
    )
    
    return {
        "format_score": format_score,
        "tables_detected": format_result.get("tables_detected", {}),
        "images_detected": format_result.get("images_detected", {}),
        "section_score": section_score,
        "detected_sections": detected_sections,
        "missing_sections": missing_sections,
        "action_score": action_score,
        "top_action_verbs": top_verbs,
        "ranked_verbs": ranked_verbs,
        "ats_score": round(ats_score, 2)
    }

if __name__ == "__main__":
    pdf_path = "src/resumes/resume_sample_3.pdf"
    ats_results = calculate_ats_score(pdf_path)
    
    print("ATS Score Breakdown:")
    for key, value in ats_results.items():
        if key == "top_action_verbs":
            print(f"{key.replace('_', ' ').title()} found in resume: {', '.join(value)}")
        elif key == "ranked_verbs":
            print("Strong Action Verbs Found (Ranked by Impact):")
            for verb, score in value[:10]:
                print(f"- {verb} (Score: {round(score * 100, 2)}%)")        
        elif key == "tables_detected" and value["has_table"]:
            print(f"Table(s) Detected on Page {value.get('page', 'Unknown')}.\nPlease remove tables for better ATS compatibility.")
        elif key == "images_detected" and value["has_images"]:
            print(f"Image(s) Detected on Page {value.get('page', 'Unknown')}.\nPlease remove images for better ATS compatibility.")
        elif key == "detected_sections":
            print(f"Detected Sections: {', '.join(value)}")
        elif key == "missing_sections":
            print(f"Missing Sections: {', '.join(value)}")
            print("Consider adding these sections to improve your resume.")
        elif key not in ["tables_detected", "images_detected"]:
            print(f"\n{key.replace('_', ' ').title()}: {value}%")

# Reference: 
# (OpenAI first prompt, 2025): Can show me an example of calculating an ATS score for a resume?
# (OpenAI last prompt, 2025): Getting error with camelot library. What does this error mean?