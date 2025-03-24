import fitz  # PyMuPDF
from lxml import html
from PIL import Image

def hocr_to_pdf(png_path, hocr_path, output_pdf_path):
    # Open the image to get its size
    img = Image.open(png_path)
    img_width, img_height = img.size

    # Create a new PDF with one page, same size as image
    doc = fitz.open()
    page = doc.new_page(width=img_width, height=img_height)

    # Insert image as background
    page.insert_image(fitz.Rect(0, 0, img_width, img_height), filename=png_path)

    # Parse HOCR
    tree = html.parse(hocr_path)
    for span in tree.xpath('//span[@class="ocrx_word"]'):
        title = span.attrib.get("title", "")
        if "bbox" not in title:
            continue
        parts = title.split(";")
        bbox_part = [p for p in parts if "bbox" in p]
        if not bbox_part:
            continue
        coords = bbox_part[0].split()[1:]
        x0, y0, x1, y1 = map(int, coords)
        word = span.text or ""

        # Add invisible text
        rect = fitz.Rect(x0, y0, x1, y1)
        page.insert_textbox(rect, word, fontsize=8, overlay=True, render_mode=3)

    doc.save(output_pdf_path)
    doc.close()

