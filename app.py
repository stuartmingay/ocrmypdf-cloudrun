from flask import Flask, request, send_file
import subprocess
import os

app = Flask(__name__)

@app.route('/ocr', methods=['POST'])
def ocr_pdf():
    if 'file' not in request.files:
        return {"error": "No file uploaded"}, 400

    pdf_file = request.files['file']
    input_path = "/app/input.pdf"
    output_path = "/app/output.pdf"

    pdf_file.save(input_path)

    # Run OCRmyPDF
    subprocess.run(["ocrmypdf", "--output-type", "pdfa", input_path, output_path])

    return send_file(output_path, as_attachment=True, mimetype='application/pdf')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))  # Default to 8080
    app.run(host='0.0.0.0', port=port)
