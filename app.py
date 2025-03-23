from flask import Flask, request, send_file
import subprocess
import os
import logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/ocr', methods=['POST'])
def ocr_pdf():
    logging.info("Received request to /ocr")

    if 'file' not in request.files:
        logging.error("No PDF file uploaded")
        return {"error": "No PDF file uploaded"}, 400

    pdf_file = request.files['file']
    input_path = "input.pdf"
    output_path = "output.pdf"
    pdf_file.save(input_path)
    logging.info(f"Saved input PDF to {input_path}")

    if 'hocr' in request.files:
        hocr_file = request.files['hocr']
        hocr_path = "input.hocr"
        hocr_file.save(hocr_path)
        logging.info(f"Saved input HOCR to {hocr_path}")

        try:
            subprocess.run([
                "ocrmypdf",
                "--output-type", "pdfa",
                "--skip-text",
                "--sidecar", hocr_path,
                input_path, output_path
            ], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"OCRmyPDF (HOCR) failed: {e}")
            return {"error": "OCRmyPDF failed with HOCR input"}, 500
    else:
        logging.info("No HOCR file found — running default OCR")
        try:
            subprocess.run([
                "ocrmypdf",
                "--output-type", "pdfa",
                input_path, output_path
            ], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"OCRmyPDF (default) failed: {e}")
            return {"error": "OCRmyPDF failed on default run"}, 500

    logging.info("Returning final PDF")
    return send_file(output_path, as_attachment=True, mimetype='application/pdf')





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

