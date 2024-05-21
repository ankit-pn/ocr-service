from PIL import Image, ImageDraw, ImageFont

# Create an image with white background
img = Image.new('RGB', (200, 100), color = (255, 255, 255))

# Initialize ImageDraw
d = ImageDraw.Draw(img)

# Add text to image
d.text((10, 10), "Hello World", fill=(0, 0, 0))

# Save the image
img.save('image.png')
