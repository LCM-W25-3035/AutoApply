import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import yake
import pymongo

nltk.download('wordnet')
nltk.download('stopwords')

job_description = cleaned_description_lemmatized
custom_kw_extractor = yake.KeywordExtractor(
    lan="en",
    n=2,
    dedupLim=0.8,
    top=40
)

# Function to clean text
def clean_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = text.translate(str.maketrans("", "", string.punctuation))  # Remove punctuation
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces

    # Optional: Remove stopwords
    stop_words = set(stopwords.words("english"))
    words = text.split()
    text = " ".join([word for word in words if word not in stop_words])

    return text
    
lemmatizer = WordNetLemmatizer()

def clean_text_with_lemmatization(text):
    text = clean_text(text)  # Apply basic cleaning
    words = text.split()
    text = " ".join([lemmatizer.lemmatize(word) for word in words])
    return text

# Retrieve all documents from the collection
jobs_cursor = collection.find({}, {"_id": 1, "Must-have Skills": 1})  # Fetch only _id and job description

# Process and update documents in MongoDB
bulk_updates = []
for job in jobs_cursor:
    job_id = job["_id"]
    job_description = job.get("Must-have Skills", "")
    categories_assigned = clean_text_with_lemmatization(job_description)
    keywords = custom_kw_extractor.extract_keywords(job_description)
    
    # Print extracted keywords
    keyword_set = {kw[0] for kw in keywords}
    keyword_set = {tuple(sorted(kw[0].split())) for kw in keywords}
    print(keyword_set)

    # Create update operation
    bulk_updates.append(
        pymongo.UpdateOne(
            {"_id": job_id},
            {"$set": {"key_word_app": keyword_set}}
        )
    )

# Upload to MongoDB
if bulk_updates:
    collection.bulk_write(bulk_updates)

print("Done ")