from PIL import Image
import fitz
import os
import logging
import pytesseract

# Set up logging
logging.basicConfig(filename='ocr_process.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Set the path to the Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

# Extract the OCR Function
def extract_text_from_image(image_path):
    try:
        # Extract text from an image using Tesseract OCR
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        logging.info(f'Text extracted from image: {image_path}')
        return text
    except Exception as e:
        logging.error(f'Error extracting text from image {image_path}: {e}')
        return ""

# Define the OCR
def read_ocr_text_from_pdf(pdf_path):
    try:
        ocr_text = ""
        with fitz.open(pdf_path) as pdf_document:
            for page_number in range(pdf_document.page_count):
                page = pdf_document[page_number]
                images = page.get_images(full=True)

                for img in images:
                    image_index = img[0]
                    base_image = pdf_document.extract_image(image_index)
                    image_bytes = base_image["image"]
                    image_path = f"temp_image_{page_number}_{image_index}.png"

                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)

                    ocr_text += extract_text_from_image(image_path)

                    # Remove temporary image file
                    os.remove(image_path)
        logging.info(f'OCR text read from PDF: {pdf_path}')
        return ocr_text
    except Exception as e:
        logging.error(f'Error reading OCR text from PDF {pdf_path}: {e}')
        return ""
