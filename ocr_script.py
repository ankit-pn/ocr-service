from PIL import Image, ImageDraw, ImageFont
import pytesseract

def create_sample_image(image_path):
    # Create an image with white background
    img = Image.new('RGB', (300, 150), color=(255, 255, 255))

    # Initialize ImageDraw
    d = ImageDraw.Draw(img)

    # Add English text to image
    d.text((10, 10), "Hello World", fill=(0, 0, 0))

    # Add Hindi text to image
    hindi_text = "नमस्ते दुनिया"
    d.text((10, 50), hindi_text, fill=(0, 0, 0))

    # Save the image
    img.save(image_path)

def perform_ocr(image_path, languages='eng+hin'):
    try:
        # Open the image file
        print(f"Opening image file: {image_path}")
        img = Image.open(image_path)
        
        # Perform OCR on the image with the specified languages
        print(f"Performing OCR with languages: {languages}")
        text = pytesseract.image_to_string(img, lang=languages)
        
        print(f"Raw OCR output: {text}")
        return text
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    image_path = "/app/sample_image.png"
    print(f"Creating sample image at: {image_path}")
    
    create_sample_image(image_path)
    
    ocr_text = perform_ocr(image_path)
    print("OCR Text:\n")
    print(ocr_text)
