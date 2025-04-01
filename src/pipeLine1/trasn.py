import pandas as pd
from langdetect import detect
from deep_translator import GoogleTranslator

from nltk.tokenize import sent_tokenize
import nltk

# Sample DataFrame
#df = pd.read_csv('FullDataset.csv')


# Function to detect language and translate if needed
def detect_and_translate(text):
    try:
        sentences = sent_tokenize(text)  # Split text into sentences
        translated_sentences = []

        for sentence in sentences:
            lang = detect(sentence)  # Detect language of each sentence
            if lang == "fr":  # Translate only if it's in French
                translated_sentence = GoogleTranslator(source="fr", target="en").translate(sentence)
                translated_sentences.append(translated_sentence)
            else:
                translated_sentences.append(sentence)  # Keep English sentences

        return " ".join(translated_sentences)  # Reconstruct text

    except Exception as e:
        return text  # Return original text if there's an error


# Apply function to the column
# df["Job Description"] = df["Job Description"].apply(detect_and_translate)

# df.to_csv('test.csv')
