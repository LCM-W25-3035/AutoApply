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
    """Ranks verbs based on similarity to strong action-oriented verbs."""
    # List of strong action-oriented verbs used as a reference for ranking
    reference_verbs = [
        "lead", "manage", "supervise", "orchestrate", "coordinate", "spearhead", "oversee", "execute", "direct",
        "develop", "design", "engineer", "build", "construct", "optimize", "architect", "automate", "troubleshoot",
        "strategize", "innovate", "pioneer", "scale", "revolutionize", "expand", "streamline", "transform",
        "resolve", "analyze", "implement", "enhance", "refine", "simplify", "boost", "elevate", "strengthen",
        "ideate", "conceive", "craft", "produce", "generate", "formulate", "compose", "invent", "visualize",
        "market", "promote", "sell", "negotiate", "engage", "captivate", "publicize", "amplify", "differentiate",
        "analyze", "evaluate", "synthesize", "interpret", "model", "quantify", "extrapolate", "benchmark"
    ]
    # Encode verbs and reference verbs using Sentence Transformers
    verb_embeddings = model.encode(verbs, convert_to_tensor=True)
    reference_embeddings = model.encode(reference_verbs, convert_to_tensor=True)
    
    # Calculate cosine similarity between input verbs and reference verbs
    similarity_scores = util.pytorch_cos_sim(verb_embeddings, reference_embeddings)

    # Sort the verbs based on their highest similarity score in descending order (strongest matches come first)
    ranked_verbs = sorted(zip(verbs, similarity_scores.max(dim=1).values.tolist()), key=lambda x: x[1], reverse=True)

    # Computes an "action score", which is the average similarity score (scaled to a percentage) of the ranked verbs 
    action_score = round(sum(score for _, score in ranked_verbs) / len(ranked_verbs) * 100, 2) if ranked_verbs else 0
    
    return ranked_verbs, action_score, [verb for verb, _ in ranked_verbs[:15]]

if __name__ == "__main__":
    pdf_path = "src/resumes/resume_sample_4.pdf"
    resume_text = extract_text_from_pdf(pdf_path)
    
    verbs = identify_action_verbs(resume_text)
    ranked_verbs, action_score, top_verbs = rank_action_verbs(verbs)
    
    print("Strong Action Verbs Found (Ranked by Impact):")
    for verb, score in ranked_verbs[:15]:
        print(f"- {verb} (Score: {round(score * 100, 2)}%)")
    
    print(f"Action-Oriented Language Score: {action_score}%")
    print(f"Top Action Verbs: {top_verbs}")

# Reference:
# (OpenAI first prompt, 2025): How can we use action verbs to improve the ATS score of a resume?
# (OpenAI last prompt, 2025): Can you show an example of extracting and ranking action verbs from a resume?