import fitz  # PyMuPDF
from lxml import html
from PIL import Image
import logging

def hocr_to_pdf(png_path, hocr_path, output_pdf_path):
    img = Image.open(png_path)
    img_width, img_height = img.size

    # Assume image and HOCR were generated from a 300 DPI source
    dpi = 300
    width_in_pts = img_width * 72 / dpi
    height_in_pts = img_height * 72 / dpi

    doc = fitz.open()
    page = doc.new_page(width=width_in_pts, height=height_in_pts)

    page.insert_image(
        fitz.Rect(0, 0, width_in_pts, height_in_pts),
        filename=png_path
    )

    # Parse HOCR and extract page bbox
    tree = html.parse(hocr_path)
    root = tree.getroot()
    page_div = root.xpath('//div[@class="ocr_page"]')
    if not page_div:
        raise ValueError("No ocr_page found in HOCR")

    page_title = page_div[0].attrib.get("title", "")

    # Extract bbox if it exists
    bbox_parts = [x.strip() for x in page_title.split(";") if "bbox" in x]

    if bbox_parts:
        try:
            parts = bbox_parts[0].split()
            if len(parts) == 5 and parts[0] == "bbox":
                _, x0, y0, x1, y1 = parts
                hocr_width = int(x1)
                hocr_height = int(y1)
                logging.info(f"HOCR bbox found: {hocr_width} x {hocr_height}")
            else:
                raise ValueError("bbox line malformed")
        except Exception as e:
            logging.info(f"Fallback: Failed to parse bbox, using image size. Error: {e}")
            hocr_width = img_width
            hocr_height = img_height
    else:
        logging.info("Fallback: No bbox found, using image size")
        hocr_width = img_width
        hocr_height = img_height

    # Compute scaling from HOCR/image pixels to PDF points
    scale_x = width_in_pts / hocr_width
    scale_y = height_in_pts / hocr_height

    # Now insert each word
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
        if not word.strip():
            continue

        # Apply scaling to fit PDF point space
        rect = fitz.Rect(
            x0 * scale_x, y0 * scale_y,
            x1 * scale_x, y1 * scale_y
        )

        # Add invisible text
        page.insert_textbox(
            rect, word,
            fontsize=8,
            fontname="helv",
            render_mode=3,
            color=(1, 1, 1),
            overlay=True
        )

    doc.save(output_pdf_path)
    doc.close()

