import json
import sys
from lxml import etree
from uuid import uuid4

def vision_to_hocr(json_data):
    html = etree.Element('html', lang='en')
    head = etree.SubElement(html, 'head')
    etree.SubElement(head, 'title').text = 'hOCR output'
    body = etree.SubElement(html, 'body')
    div = etree.SubElement(body, 'div', attrib={'class': 'ocr_page', 'id': 'page_1'})

    for page in json_data.get('fullTextAnnotation', {}).get('pages', []):
        for block in page.get('blocks', []):
            for paragraph in block.get('paragraphs', []):
                for word in paragraph.get('words', []):
                    word_text = ''.join([symbol['text'] for symbol in word.get('symbols', [])])
                    bbox = word.get('boundingBox', {})
                    if 'vertices' in bbox and len(bbox['vertices']) == 4:
                        bbox_coords = [
                            bbox['vertices'][0]['x'], bbox['vertices'][0]['y'],
                            bbox['vertices'][2]['x'], bbox['vertices'][2]['y']
                        ]
                        span = etree.SubElement(
                            div, 'span',
                            attrib={
                                'class': 'ocrx_word',
                                'id': f"word_{uuid4().hex[:8]}",
                                'title': f"bbox {bbox_coords[0]} {bbox_coords[1]} {bbox_coords[2]} {bbox_coords[3]}"
                            }
                        )
                        span.text = word_text

    return etree.tostring(html, pretty_print=True, encoding='unicode')

if __name__ == "__main__":
    with open(sys.argv[1], 'r') as f:
        vision_json = json.load(f)
    hocr_output = vision_to_hocr(vision_json)
    print(hocr_output)

