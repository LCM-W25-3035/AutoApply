import pdfplumber
import camelot
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

def detect_text_based_tables(pdf_path):
    """Detects tables in a PDF using pdfplumber (text-based tables)."""
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            if tables and any(len(row) > 1 for table in tables for row in table):
                return {"has_table": True, "page": page_num + 1, "method": "pdfplumber"}
    return {"has_table": False, "method": "pdfplumber"}


def detect_structured_tables(pdf_path):
    """Detects structured tables in a PDF using Camelot."""
    try:
        tables = camelot.read_pdf(pdf_path, pages='all')
        if len(tables) > 0:
            return {"has_table": True, "method": "Camelot"}
    except Exception as e:
        print(f"Camelot error: {e}")
    return {"has_table": False, "method": "Camelot"}


def detect_image_based_tables(pdf_path):
    """Detects tables in image-based PDFs using OCR (pytesseract)."""
    images = convert_from_path(pdf_path)
    for i, img in enumerate(images):
        text = pytesseract.image_to_string(img)
        if "|" in text or "----" in text:  # Common table markers
            return {"has_table": True, "page": i + 1, "method": "OCR"}
    return {"has_table": False, "method": "OCR"}


def detect_images_in_pdf(pdf_path):
    """Detects if a PDF contains images, which may not be ATS-friendly."""
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            if page.images:
                return {"has_images": True, "page": page_num + 1}
    return {"has_images": False}


def detect_tables_in_resume(pdf_path):
    """Runs all three detection methods to check for tables in a resume PDF."""
    text_table_result = detect_text_based_tables(pdf_path)
    if text_table_result["has_table"]:
        return text_table_result

    structured_table_result = detect_structured_tables(pdf_path)
    if structured_table_result["has_table"]:
        return structured_table_result

    image_table_result = detect_image_based_tables(pdf_path)
    if image_table_result["has_table"]:
        return image_table_result

    return {"has_table": False, "method": "None"}

def detect_bad_formatting(pdf_path):
    """Checks for common ATS-unfriendly formatting issues (tables, images)."""
    table_result = detect_tables_in_resume(pdf_path)
    image_result = detect_images_in_pdf(pdf_path)
    return {"tables_detected": table_result, "images_detected": image_result}

if __name__ == "__main__":
    pdf_path = "src\\resumes\\resume_sample_bad_format.pdf"
    result = detect_bad_formatting(pdf_path)

    if result["tables_detected"]["has_table"]:
        print(f"Resume contains a table on Page {result['tables_detected'].get('page', 'Unknown')}.")
    if result["images_detected"]["has_images"]:
        print(f"Resume contains an image on Page {result['images_detected'].get('page', 'Unknown')}.")
    if not result["tables_detected"]["has_table"] and not result["images_detected"]["has_images"]:
        print("Resume is ATS-friendly (no tables or images).")

# Reference
# (OpenAI first prompt, 2025): How can we use ATS score for the applicant pov? 
# (OpenAI last prompt, 2025): Is there another function for detecting images? or any other bad format?