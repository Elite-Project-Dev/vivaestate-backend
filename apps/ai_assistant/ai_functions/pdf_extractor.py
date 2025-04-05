import re

import pdfplumber
import pytesseract
from pdf2image import convert_from_path


def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF using pdfplumber.
    If the PDF is scanned (image-based), OCR is used instead.
    """
    extracted_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                extracted_text.append(text)
    full_text = "\n".join(extracted_text)
    # if text extration fails use OCR
    if not full_text.strip():
        return extract_text_from_scanned_pdf(pdf_path)
    return clean_text(full_text)


def extract_text_from_scanned_pdf(pdf_path):
    """
    uses orc to  extract text from pdf"""
    pages = convert_from_path(pdf_path)
    text = [pytesseract.image_to_string(page) for page in pages]
    return clean_text("\n".join(text))


def clean_text(text):
    """
    Cleans extracted text by removing extra spaces, newlines, non-ASCII characters,
    and fixing common OCR issues.
    """
    text = re.sub(r"\s+", " ", text)  # Remove excessive spaces
    text = re.sub(r"[^\x00-\x7F]+", "", text)  # Remove non-ASCII characters
    text = re.sub(r"([a-zA-Z])\1{2,}", r"\1", text)  # Fix repeated letters
    text = re.sub(r"//", ", ", text)  # Replace slashes with commas
    return text.strip()
