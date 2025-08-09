import fitz  # PyMuPDF
import docx
import pandas as pd
import pytesseract
from PIL import Image
import io

def extract_text_from_file(file, file_type):
    text = ""
    if file_type == "pdf":
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()
    elif file_type == "docx":
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif file_type == "txt":
        text = file.read().decode("utf-8")
    elif file_type == "xlsx":
        df = pd.read_excel(file)
        text = df.to_string()
    elif file_type in ["png", "jpg", "jpeg"]:
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
    return text
