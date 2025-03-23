FROM ubuntu:22.04

# Set working directory in container
WORKDIR /ocrmypdf-cloudrun

# Install system dependencies and OCR tools
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv ocrmypdf tesseract-ocr && \
    rm -rf /var/lib/apt/lists/*

# Set up virtual environment and install Python packages
RUN python3 -m venv /ocrmypdf-cloudrun/venv && \
    /ocrmypdf-cloudrun/venv/bin/pip install --no-cache-dir flask requests lxml

# Set environment variable so virtualenv is active by default
ENV PATH="/ocrmypdf-cloudrun/venv/bin:$PATH"

# Copy app files into container
COPY app.py vision_to_hocr.py ./

# Launch Flask app
CMD ["/ocrmypdf-cloudrun/venv/bin/python3", "app.py"]

