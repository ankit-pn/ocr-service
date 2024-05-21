import pytesseract
from PIL import Image
import sys

def perform_ocr(image_path, languages='eng+hin+urd'):
    try:
        # Open the image file
        img = Image.open(image_path)
        # Perform OCR on the image with the specified languages
        text = pytesseract.image_to_string(img, lang=languages)
        return text
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ocr_script.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    ocr_text = perform_ocr(image_path)
    print("OCR Text:\n")
    print(ocr_text)
