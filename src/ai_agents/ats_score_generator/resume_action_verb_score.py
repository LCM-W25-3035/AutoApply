import spacy
from pdfminer.high_level import extract_text
from sentence_transformers import SentenceTransformer, util

# Load NLP Model
nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("all-mpnet-base-v2")


def extract_text_from_pdf(pdf_path):
    """Extracts raw text from the PDF."""
    return extract_text(pdf_path)


def identify_action_verbs(resume_text):
    """Identifies action-oriented verbs dynamically using NLP."""
    doc = nlp(resume_text)
    verbs_found = set()
    
    for token in doc:
        if token.pos_ == "VERB" and token.dep_ in {"ROOT", "advcl", "xcomp"}:  
            verbs_found.add(token.lemma_)
    
    return list(verbs_found)


def rank_action_verbs(verbs):
    """Ranks verbs based on similarity to strong action-oriented verbs using embeddings."""
    reference_verbs = ["develop", "lead", "execute", "manage", "design", "launch", "streamline", "orchestrate"]
    
    verb_embeddings = model.encode(verbs, convert_to_tensor=True)
    reference_embeddings = model.encode(reference_verbs, convert_to_tensor=True)
    
    similarity_scores = util.pytorch_cos_sim(verb_embeddings, reference_embeddings)
    ranked_verbs = sorted(zip(verbs, similarity_scores.max(dim=1).values.tolist()), key=lambda x: x[1], reverse=True)
    
    action_score = round(sum(score for _, score in ranked_verbs) / len(ranked_verbs) * 100, 2) if ranked_verbs else 0
    
    return ranked_verbs, action_score

if __name__ == "__main__":
    pdf_path = "src\\resumes\\resume_sample_4.pdf"
    resume_text = extract_text_from_pdf(pdf_path)
    
    verbs = identify_action_verbs(resume_text)
    ranked_verbs, action_score = rank_action_verbs(verbs)
    
    print("Strong Action Verbs Found (Ranked by Impact):")
    for verb, score in ranked_verbs[:10]:  # Show top 10 ranked verbs
        print(f"- {verb} (Score: {round(score * 100, 2)}%)")
    
    print(f"Action-Oriented Language Score: {action_score}%")

# Reference:
# (OpenAI first prompt, 2025): How can we use action verbs to improve the ATS score of a resume?
# (OpenAI last prompt, 2025): Suggest ways to calculate action verb scores for a resume.