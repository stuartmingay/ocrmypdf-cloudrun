FROM ubuntu:22.04

WORKDIR /app

# Install system dependencies, including Python, pip, and OCRmyPDF
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv ocrmypdf tesseract-ocr && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python3 -m venv /app/venv && /app/venv/bin/pip install --no-cache-dir flask requests lxml

# Set environment variables to use the virtual environment
ENV PATH="/app/venv/bin:$PATH"

COPY app.py vision_to_hocr.py /app/

# Use the correct full Python path explicitly
CMD ["/app/venv/bin/python3", "/app/app.py"]
