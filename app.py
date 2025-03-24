from flask import Flask, request, send_file
import subprocess
import os
import logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/ocr', methods=['POST'])
def ocr_pdf():
    logging.info("Received request to /ocr")

    if 'file' not in request.files or 'hocr' not in request.files:
        logging.error("Missing file(s): need both PNG image and HOCR")
        return {"error": "PNG image and HOCR file are required"}, 400

    image_file = request.files['file']
    hocr_file = request.files['hocr']

    image_path = "input.png"
    hocr_path = "input.hocr"
    output_pdf_path = "output.pdf"

    image_file.save(image_path)
    hocr_file.save(hocr_path)

    try:
        with open(output_pdf_path, "wb") as output_pdf:
            subprocess.run(
                ["hocr-pdf", ".", "-i", image_path],
                stdin=open(hocr_path, "rb"),
                stdout=output_pdf,
                check=True
            )
    except subprocess.CalledProcessError as e:
        logging.error(f"hocr-pdf failed: {e}")
        return {"error": "HOCR-PDF failed"}, 500

    logging.info("Returning final PDF")
    return send_file(output_pdf_path, as_attachment=True, mimetype='application/pdf')




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

