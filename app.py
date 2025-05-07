import os
import logging
import subprocess
import json
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

    image_path = "image.png"
    hocr_path = "input.hocr"
    output_path = "output.pdf"

    try:
        # Ensure image is provided
        if 'image' not in request.files:
            return jsonify({"error": "Missing image file"}), 400
        image_file = request.files['image']
        image_file.save(image_path)
        logging.info("Saved image to image.png")

        # Ensure hOCR is provided
        if 'hocr' not in request.files:
            return jsonify({"error": "Missing hOCR file"}), 400
        hocr_file = request.files['hocr']
        hocr_file.save(hocr_path)
        logging.info("Saved hOCR to input.hocr")

        # Generate PDF with embedded HOCR text layer
        hocr_to_pdf(image_path, hocr_path, output_path)
        logging.info("Successfully created searchable PDF")

        return send_file(output_path, as_attachment=True, mimetype='application/pdf')

    except Exception as ex:
        logging.error(f"Error in /ocr: {ex}")
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

