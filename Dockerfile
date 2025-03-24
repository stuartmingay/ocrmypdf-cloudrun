FROM ubuntu:22.04

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    hocr-tools imagemagick \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Optional: remove ocrmypdf from here if it was included before

# Set up Python virtual environment
RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir flask requests lxml

ENV PATH="/app/venv/bin:$PATH"

COPY app.py vision_to_hocr.py /app/

CMD ["python3", "/app/app.py"]

