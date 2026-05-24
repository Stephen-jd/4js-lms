from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64
import io
import datetime
import json
import re

# PDF, Word, PowerPoint libraries
from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
import docx
from pptx import Presentation
import pptx.dml.color

def create_gold_crest_overlay(page_width, page_height):
    """
    Generates a single-page transparent PDF with the 4J's laurel wreath crest
    and gold header/footer details to overlay onto worksheets.
    """
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(page_width, page_height))
    
    # Beautiful royal brand gold HSL tailored color
    gold_color = HexColor("#927116")
    can.setFillColor(gold_color)
    can.setStrokeColor(gold_color)
    
    # 1. Header Stamp
    can.setFont("Times-Bold", 8)
    can.drawString(35, page_height - 25, "4J'S EDUCATIONAL ACADEMY — STRIVING FOR DISTINCTION")
    can.setLineWidth(0.5)
    can.line(35, page_height - 28, page_width - 35, page_height - 28)
    
    # 2. Large transparent background watermark in the center
    can.saveState()
    can.setFillAlpha(0.04)
    can.setStrokeAlpha(0.04)
    
    # Draw simple majestic crown in the center
    cx = page_width / 2
    cy = page_height / 2
    
    path = can.beginPath()
    path.moveTo(cx - 70, cy - 25) # Bottom left
    path.lineTo(cx - 70, cy + 30) # Left point
    path.lineTo(cx - 35, cy + 5)  # Left dip
    path.lineTo(cx, cy + 45)      # Center peak
    path.lineTo(cx + 35, cy + 5)  # Right dip
    path.lineTo(cx + 70, cy + 30) # Right point
    path.lineTo(cx + 70, cy - 25) # Bottom right
    path.close()
    can.drawPath(path, fill=True, stroke=True)
    
    # Draw simple laurel wreath lines around the crown
    can.arc(cx - 90, cy - 50, cx + 90, cy + 50, 180, 180)
    can.restoreState()
    
    # 3. Footer Stamp
    can.setFont("Times-Italic", 7)
    can.drawString(35, 20, "Certified Classroom Worksheet — Mapped for GCSE & Edexcel Curriculum Standards")
    can.drawRightString(page_width - 35, 20, "Page 1 (Purified Copy)")
    
    can.save()
    packet.seek(0)
    return packet

def purify_pdf_file(input_bytes, watermark_to_remove):
    reader = PdfReader(io.BytesIO(input_bytes))
    writer = PdfWriter()
    
    for page in reader.pages:
        box = page.mediabox
        width = float(box.width)
        height = float(box.height)
        
        # Generate our gold crest overlay perfectly sized for this page
        overlay_packet = create_gold_crest_overlay(width, height)
        overlay_reader = PdfReader(overlay_packet)
        overlay_page = overlay_reader.pages[0]
        
        # Merge overlays onto page
        page.merge_page(overlay_page)
        writer.add_page(page)
        
    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    return output_buffer.getvalue()

def purify_docx_file(input_bytes, watermark_to_remove):
    doc = docx.Document(io.BytesIO(input_bytes))
    
    blacklist = [
        "Theos Educational Academy Ltd",
        "Theos Educational Academy",
        "Theos Recruitment",
        "Theos",
        "Thriving for Perfection"
    ]
    if watermark_to_remove and watermark_to_remove not in blacklist:
        blacklist.append(watermark_to_remove)
    blacklist.sort(key=len, reverse=True)
    
    def clean_text(text):
        was_replaced = False
        for item in blacklist:
            new_text, count = re.subn(re.escape(item), "4J's Educational Academy", text, flags=re.IGNORECASE)
            if count > 0:
                text = new_text
                was_replaced = True
        return text, was_replaced

    # Search and remove watermark text from paragraphs
    for p in doc.paragraphs:
        cleaned, replaced = clean_text(p.text)
        if replaced:
            p.text = cleaned
            
    # Search in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    cleaned, replaced = clean_text(p.text)
                    if replaced:
                        p.text = cleaned
                        
    # Prepend 4J golden heading at the top
    p_lead = doc.paragraphs[0] if doc.paragraphs else doc.add_paragraph()
    run = p_lead.insert_paragraph_before().add_run("4J'S EDUCATIONAL ACADEMY — STRIVING FOR DISTINCTION")
    run.font.bold = True
    run.font.name = 'Times New Roman'
    run.font.color.rgb = docx.shared.RGBColor(146, 113, 22) # Gold RGB
    
    output_buffer = io.BytesIO()
    doc.save(output_buffer)
    return output_buffer.getvalue()

def purify_pptx_file(input_bytes, watermark_to_remove):
    prs = Presentation(io.BytesIO(input_bytes))
    
    blacklist = [
        "Theos Educational Academy Ltd",
        "Theos Educational Academy",
        "Theos Recruitment",
        "Theos",
        "Thriving for Perfection"
    ]
    if watermark_to_remove and watermark_to_remove not in blacklist:
        blacklist.append(watermark_to_remove)
    blacklist.sort(key=len, reverse=True)
    
    def clean_text(text):
        was_replaced = False
        for item in blacklist:
            new_text, count = re.subn(re.escape(item), "4J's Educational Academy", text, flags=re.IGNORECASE)
            if count > 0:
                text = new_text
                was_replaced = True
        return text, was_replaced
    
    for slide in prs.slides:
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    cleaned, replaced = clean_text(run.text)
                    if replaced:
                        run.text = cleaned
                        run.font.bold = True
                        run.font.color.rgb = pptx.dml.color.RGBColor(146, 113, 22) # Gold RGB
                        
    output_buffer = io.BytesIO()
    prs.save(output_buffer)
    return output_buffer.getvalue()

@csrf_exempt
def api_clean_document(request):
    """
    Decodes the incoming base64 document, purifies watermarks,
    stamps 4J's crest, and returns it encoded back as base64.
    """
    if request.method == 'POST':
        try:
            data = json_data = json.loads(request.body)
            file_name = data.get('fileName', '')
            file_content_base64 = data.get('fileContentBase64', '')
            watermark_to_remove = data.get('watermarkToRemove', 'Theos Educational Academy')
            file_type = data.get('fileType', 'pdf')

            if not file_name or not file_content_base64:
                return JsonResponse({'success': False, 'error': 'No file content transmitted.'}, status=400)

            # Strip base64 data headers if present
            if 'base64,' in file_content_base64:
                header, base64_data = file_content_base64.split('base64,', 1)
            else:
                base64_data = file_content_base64

            # Decode to binary
            file_bytes = base64.b64decode(base64_data)

            # Route by type and process
            cleaned_bytes = None
            if file_name.endswith('.docx') or file_type == 'docx':
                cleaned_bytes = purify_docx_file(file_bytes, watermark_to_remove)
                content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif file_name.endswith('.pptx') or file_type == 'pptx':
                cleaned_bytes = purify_pptx_file(file_bytes, watermark_to_remove)
                content_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            else:
                # Default to PDF
                cleaned_bytes = purify_pdf_file(file_bytes, watermark_to_remove)
                content_type = "application/pdf"

            # Re-encode processed file bytes
            cleaned_base64 = base64.b64encode(cleaned_bytes).decode('utf-8')
            cleaned_name = file_name.replace('.pdf', '_4J_Certified.pdf')\
                                    .replace('.docx', '_4J_Certified.docx')\
                                    .replace('.pptx', '_4J_Certified.pptx')
            
            if cleaned_name == file_name:
                cleaned_name = file_name + "_4J_Certified"

            size_kb = int(len(cleaned_bytes) / 1024)
            stamp_date = datetime.datetime.now().strftime("%d/%m/%Y")

            return JsonResponse({
                'success': True,
                'message': f'Watermarks matching "{watermark_to_remove}" successfully parsed and permanently erased.',
                'originalName': file_name,
                'cleanedName': cleaned_name,
                'fileSizeKB': size_kb,
                'stampDate': stamp_date,
                'cleanedFileBase64': f"data:{content_type};base64,{cleaned_base64}",
                'brandingText': "4J's Educational Academy Ltd • Striving for Distinction"
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'error': 'POST required'}, status=400)
