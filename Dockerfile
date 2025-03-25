FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required for PyMuPDF (fitz), PIL, and lxml
RUN apt-get update && apt-get install -y \
    libjpeg-dev libopenjp2-7 libtiff-dev libpng-dev \
    libxml2 libxslt1-dev libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app.py inject_hocr.py vision_to_hocr.py /app/

CMD ["python", "app.py"]

