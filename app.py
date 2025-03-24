from flask import Flask, request, send_file
import subprocess
import os
import logging
from inject_hocr import hocr_to_pdf

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/ocr', methods=['POST'])
def create_pdf():
    if 'file' not in request.files or 'hocr' not in request.files:
        return {"error": "PNG image and HOCR file required"}, 400

    image_file = request.files['file']
    hocr_file = request.files['hocr']

    image_path = "input.png"
    hocr_path = "input.hocr"
    output_pdf_path = "output.pdf"

    image_file.save(image_path)
    hocr_file.save(hocr_path)

    try:
        hocr_to_pdf(image_path, hocr_path, output_pdf_path)
    except Exception as e:
        return {"error": str(e)}, 500

    return send_file(output_pdf_path, mimetype='application/pdf', as_attachment=True)


@app.route('/convert_hocr', methods=['POST'])
def convert_hocr():
    if 'vision_json' not in request.files:
        return {"error": "No vision_json file uploaded"}, 400

    json_file = request.files['vision_json']
    json_path = "input.json"
    hocr_path = "output.hocr"

    json_file.save(json_path)

    # Run the HOCR conversion script
    with open(hocr_path, "w") as hocr_output:
        subprocess.run(["python3", "vision_to_hocr.py", json_path], stdout=hocr_output, check=True)

    return send_file(hocr_path, as_attachment=True, mimetype='text/html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))  # Default to 8080
    app.run(host='0.0.0.0', port=port)

