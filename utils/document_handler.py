import fitz  # PyMuPDF
import docx
import pandas as pd
from PIL import Image
import pytesseract
import io

def extract_text_from_file(file, file_type):
    if file_type == "pdf":
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return "\n".join(page.get_text() for page in doc)
    elif file_type == "docx":
        doc = docx.Document(file)
        return "\n".join(p.text for p in doc.paragraphs)
    elif file_type == "txt":
        return file.read().decode("utf-8")
    elif file_type == "xlsx":
        df = pd.read_excel(file)
        return df.to_string()
    elif file_type in ["png", "jpg", "jpeg"]:
        image = Image.open(io.BytesIO(file.read()))
        return pytesseract.image_to_string(image)
    return ""
