import os
import time
import requests
import pytesseract
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Timer
from concurrent.futures import Executor
import json
# Configuration
images_directory = "/app/images"
ocr_threads = int(os.getenv("OCR_THREADS", 4))
redis_api_password = os.getenv("REDIS_API_PASSWORD")
redis_api_domain = os.getenv("REDIS_API_DOMAIN")
notification_api_domain=os.getenv("NOTIFICATION_API_DOMAIN")

redis_get_url = f"https://{redis_api_domain}/get/"
redis_set_url = f"https://{redis_api_domain}/set/"
notify_url = f"http://host.docker.internal:8117/notify"
dbsize_url = f"https://{redis_api_domain}/dbsize/"

processed_images_count = 0
total_images_count = 0



class ImageHandler(FileSystemEventHandler):
    def __init__(self, executor):
        self.executor = executor

    def on_created(self, event):
        if event.is_directory:
            return
        # Extract file extension and check if it's an image file
        _, file_extension = os.path.splitext(event.src_path)
        if file_extension.lower() in ['.jpg', '.jpeg', '.png']:
            self.executor.submit(process_image, event.src_path)
            update_total_images_count()

def process_image(image_path):
    global processed_images_count
    filename = os.path.basename(image_path)
    key = os.path.splitext(filename)[0]
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    } 
    data = {
        "key": key,
        "db": 0,
        "password": redis_api_password
    }
    # Check if the image has already been processed
    response = requests.get(redis_get_url, headers=headers, json=data)
    if response.status_code == 200:
#        print(f"Image {filename} has already been processed.")
        return
    
    # Perform OCR
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='eng+hin')
#        print(f"OCR for {filename}: {text}")
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        # Post OCR data to an API (example endpoint)
        post_data = {
            "key": key,
            "value": text,
            "db": 0,
            "password": redis_api_password
        }
        post_response = requests.post(redis_set_url,headers=headers, json=post_data)
        if post_response.status_code == 200:
#            print(f"OCR data for {filename} posted successfully.")
            processed_images_count += 1
        else:
            print(f"Failed to post OCR data for {filename}: {post_response.text}")
    except Exception as e:
        print(f"Error processing {filename}: {e}")

def scan_directory(executor: Executor, path: str):
    global total_images_count
    valid_extensions = ('.jpg', '.jpeg', '.png')  # Define allowed image formats
    
    for root, dirs, files in os.walk(path, topdown=True):
        for name in files:
            if name.lower().endswith(valid_extensions):  # Check if the file is a valid image format
                file_path = os.path.join(root, name)
                executor.submit(process_image, file_path)
            else:
                continue
               # print(f"Ignored non-image file: {name}")  # Optional: log ignored files

        for name in dirs:
            dir_path = os.path.join(root, name)
            if not os.access(dir_path, os.R_OK):
                print(f"Permission denied: {dir_path}")
                continue

def update_total_images_count():
    global total_images_count
    image_extensions = ['.jpg', '.jpeg', '.png']
    total_images_count = sum(
        len([file for file in files if os.path.splitext(file)[1].lower() in image_extensions])
        for r, d, files in os.walk(images_directory)
    )

def send_notification():
    global processed_images_count, total_images_count
    try:
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        } 
        # Get total number of processed images from the database
        response = requests.get(dbsize_url,headers=headers, json={"password": redis_api_password,"db":0})
        if response.status_code == 200:
            total_processed_images = response.json().get('dbsize', 0)
        else:
            total_processed_images = 0

        # Notify API
        notify_data = {
            "processed_images_count": processed_images_count,
            "total_images_count": total_images_count,
            "total_processed_images": total_processed_images
        }
        notify_response = requests.post(notify_url, json=notify_data)
        if notify_response.status_code == 200:
            print("Notification sent successfully.")
        else:
            print(f"Failed to send notification: {notify_response.text}")

        # Reset the counter for the next hour
        processed_images_count = 0
    except Exception as e:
        print(f"Error sending notification: {e}")

    # Schedule the next notification
    Timer(3600, send_notification).start()
    
if __name__ == "__main__":
    print("Processes has started")
    executor = ThreadPoolExecutor(max_workers=ocr_threads)
    
    Timer(3600, send_notification).start()
    # Initial scan of all directories and subdirectories
    scan_directory(executor, images_directory)

    event_handler = ImageHandler(executor)
    observer = Observer()
    observer.schedule(event_handler, path=images_directory, recursive=True)
    
    observer.start()
    print(f"Started monitoring {images_directory} with {ocr_threads} threads.")

    # Update the total image count initially
    update_total_images_count()

    # Start the notification timer
    
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
