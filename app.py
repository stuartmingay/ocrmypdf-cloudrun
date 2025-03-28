import os
import logging
import subprocess
from flask import Flask, request, send_file, jsonify
from google.cloud import storage
from inject_hocr import hocr_to_pdf

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

def download_from_gcs(gcs_url, local_path):
    if not gcs_url.startswith("gs://"):
        raise ValueError("Invalid GCS URL")
    _, bucket_name, *blob_parts = gcs_url.split("/")
    blob_name = "/".join(blob_parts)
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(local_path)
    logging.info(f"Downloaded {gcs_url} to {local_path}")

@app.route('/ocr', methods=['POST'])
def create_pdf():
    logging.info("Received request to /ocr")

    input_path = "input.pdf"
    output_path = "output.pdf"
    image_path = "image.png"  # Used if hocr injection is needed
    hocr_path = "input.hocr"

    try:
        # Case 1: Direct file upload
        if 'file' in request.files:
            pdf_file = request.files['file']
            pdf_file.save(input_path)
            logging.info("PDF uploaded via multipart form")

        # Case 2: JSON with GCS URL
        elif request.is_json:
            data = request.get_json()
            pdf_url = data.get("pdf_url")
            if not pdf_url:
                return jsonify({"error": "Missing pdf_url"}), 400
            download_from_gcs(pdf_url, input_path)

        else:
            return jsonify({"error": "No PDF provided"}), 400

        # Optional: HOCR file provided
        if 'hocr' in request.files:
            hocr_file = request.files['hocr']
            hocr_file.save(hocr_path)
            logging.info("HOCR file uploaded")

            # Convert PDF to image (PNG) for overlay
            subprocess.run([
                "convert", "-density", "300", input_path,
                "-background", "white", "-alpha", "remove", image_path
            ], check=True)
            logging.info("Converted PDF to PNG")

            # Run HOCR injection
            hocr_to_pdf(image_path, hocr_path, output_path)
            logging.info("Generated searchable PDF with HOCR overlay")

        else:
            logging.info("No HOCR provided – running OCRmyPDF normally")
            subprocess.run([
                "ocrmypdf",
                "--output-type", "pdfa",
                input_path, output_path
            ], check=True)

        return send_file(output_path, as_attachment=True, mimetype='application/pdf')

    except subprocess.CalledProcessError as e:
        logging.error(f"OCR or conversion failed: {e}")
        return jsonify({"error": "OCR processing failed"}), 500
    except Exception as ex:
        logging.error(f"Unexpected error: {ex}")
        return jsonify({"error": str(ex)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

