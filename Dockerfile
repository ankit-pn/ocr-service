FROM python:3.9-slim

WORKDIR /app

COPY ocr_service.py /app
COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "ocr_service.py"]
