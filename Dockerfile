FROM ubuntu:22.04

WORKDIR /app

# Install dependencies and hocr-pdf from source
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    git imagemagick tesseract-ocr \
 && rm -rf /var/lib/apt/lists/* \
 && git clone https://github.com/tmbdev/hocr-tools.git /hocr-tools \
 && cd /hocr-tools && python3 setup.py install

# Set up virtual environment for Flask and related Python packages
RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir flask requests lxml

ENV PATH="/app/venv/bin:$PATH"

COPY app.py vision_to_hocr.py /app/

CMD ["python3", "/app/app.py"]

