import re
import html
from fpdf import FPDF

def clean_text(text):
    """
    Clean the extracted resume text by removing unwanted characters,
    fixing encoding issues, and handling HTML entities.
    
    Parameters:
        text (str): Raw resume text to be cleaned.
    
    Returns:
        str: Cleaned resume text.
    """
    # Decode HTML entities
    text = html.unescape(text)

    # Remove strange characters and encoding problems
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()  # Remove leading and trailing spaces

    return text

def clean_resume_from_file(file_path):
    """Read a resume from a file and clean the text."""
    try:
        with open(file_path, "r", encoding="utf-8-sig") as file:
            raw_text = file.read()
            cleaned_text = clean_text(raw_text)
            return cleaned_text
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def save_text_as_pdf(text, output_file_path):
    """Save cleaned text into a PDF file."""
    # Initialize PDF object
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Set font for the PDF
    pdf.set_font("Arial", size=12)

    # Add cleaned text to the PDF (wrap the text to avoid overflow)
    pdf.multi_cell(0, 10, text)  # Multi-cell automatically wraps text

    # Save the PDF to a file
    pdf.output(output_file_path)
    print(f"PDF saved as {output_file_path}")

def main():
    # Path to the resume file you want to clean
    input_file_path = "resume_sample.txt"  # Replace with your resume file path
    output_pdf_path = "cleaned_resume.pdf"  # The path where you want to save the cleaned resume PDF
    
    # Clean the resume text from the file
    cleaned_text = clean_resume_from_file(input_file_path)
    
    if cleaned_text:
        # Save the cleaned resume text to PDF
        save_text_as_pdf(cleaned_text, output_pdf_path)

if __name__ == "__main__":
    main()
