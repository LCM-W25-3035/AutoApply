import pdfplumber
import camelot
import pytesseract

def detect_text_based_tables(pdf_path):
    """Detects tables in a PDF using pdfplumber (text-based tables)."""
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            if tables and any(len(row) > 1 for table in tables for row in table):
                return {"has_table": True, "page": page_num + 1}
    return {"has_table": False}

def detect_structured_tables(pdf_path):
    """Detects structured tables in a PDF using Camelot."""
    try:
        tables = camelot.read_pdf(pdf_path, pages='all')
        if len(tables) > 0:
            return {"has_table": True}
    except Exception:
        pass
    return {"has_table": False}

def detect_image_based_tables(pdf_path):
    """Detects tables in image-based PDFs using OCR (pytesseract)."""
    # Use pdfplumber to extract images and then apply OCR
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            if page.images:
                for img in page.images:
                    # Extract image and apply OCR
                    x0, y0, x1, y1 = img["x0"], img["y0"], img["x1"], img["y1"]
                    cropped_image = page.within_bbox((x0, y0, x1, y1)).to_image()
                    text = pytesseract.image_to_string(cropped_image)
                    if "|" in text or "----" in text:  # Common table markers
                        return {"has_table": True, "page": page_num + 1}
    return {"has_table": False}

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
    
    return {"has_table": False}

def check_resume_format(pdf_path):
    """Checks for common ATS-unfriendly formatting issues (tables, images) and returns a score."""
    table_result = detect_tables_in_resume(pdf_path)
    image_result = detect_images_in_pdf(pdf_path)
    
    # Scoring logic
    format_score = 100
    if table_result["has_table"]:
        format_score -= 50  # Deduct 50 points for tables as they are not ATS-friendly
    if image_result["has_images"]:
        format_score -= 30  # Deduct 30 points for images as they are not ATS-friendly
    
    return {
        "tables_detected": table_result,
        "images_detected": image_result,
        "format_score": max(format_score, 0)  # Ensure score is not negative
    }

if __name__ == "__main__":
    pdf_path = "src/resumes/resume_sample_bad_format.pdf"
    result = check_resume_format(pdf_path)
    
    if result["tables_detected"]["has_table"]:
        print(f"Resume contains a table on Page {result['tables_detected'].get('page', 'Unknown')}.")
    if result["images_detected"]["has_images"]:
        print(f"Resume contains an image on Page {result['images_detected'].get('page', 'Unknown')}.")
    if not result["tables_detected"]["has_table"] and not result["images_detected"]["has_images"]:
        print("Resume is ATS-friendly (no tables or images).")
    
    print(f"Resume Formatting Score: {result['format_score']}%")

# Reference
# (OpenAI first prompt, 2025): How do ATS systems evaluate resume formatting? 
# (OpenAI last prompt, 2025): Is there another function for detecting images? How can I detect images in a pdf file?