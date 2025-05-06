import os
import logging
import subprocess
from flask import Flask, request, send_file, jsonify
from google.cloud import storage
from inject_hocr import hocr_to_pdf
from vision_to_hocr import vision_to_hocr  # NEW

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
    image_path = "image.png"
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

            subprocess.run([
                "convert", "-density", "300", input_path,
                "-background", "white", "-alpha", "remove", image_path
            ], check=True)
            logging.info("Converted PDF to PNG")

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

@app.route('/converthocr', methods=['POST'])
def convert_hocr():
    logging.info("Received request to /converthocr")
    try:
        if 'vision_json' not in request.files:
            return jsonify({"error": "Missing vision_json file"}), 400

        vision_file = request.files['vision_json']
        json_data = json.load(vision_file)
        hocr_output = vision_to_hocr(json_data)

        # Return raw HTML or downloadable file — pick one
        return hocr_output, 200, {
            'Content-Type': 'text/html; charset=utf-8'
        }

        # Optional: return as downloadable file instead
        # response = make_response(hocr_output)
        # response.headers.set('Content-Type', 'text/html')
        # response.headers.set('Content-Disposition', 'attachment', filename='output.hocr')
        # return response

    except Exception as ex:
        logging.error(f"Error in /converthocr: {ex}")
        return jsonify({"error": str(ex)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

