from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from resources.models import SyllabusTracker, ResourceItem
import json
import io
import zipfile
import re
import random

# PDF, Word, and PowerPoint imports
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import docx
from pptx import Presentation
from pptx.util import Inches, Pt
import pptx.dml.color

@csrf_exempt
def api_update_syllabus(request):
    """
    Saves or updates curriculum checkpoints for GCSE/Edexcel boards in the database.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Trainer authorization required.'}, status=403)
        try:
            data = json.loads(request.body)
            slot_id = data.get('id')
            status = data.get('status')
            
            try:
                # Retrieve existing syllabus topic
                topic = SyllabusTracker.objects.get(id=slot_id)
                topic.status = status
                topic.covered_by = request.user.get_full_name() or request.user.username
                topic.save()
            except SyllabusTracker.DoesNotExist:
                # If topic doesn't exist yet, register a new one dynamically
                topic = SyllabusTracker.objects.create(
                    board=data.get('board', 'GCSE'),
                    year_level=data.get('year', 'Year 8'),
                    subject=data.get('subject', 'Maths'),
                    topic=data.get('topic', 'General Revision'),
                    subtopic=data.get('subtopic', ''),
                    status=status,
                    covered_by=request.user.get_full_name() or request.user.username
                )

            return JsonResponse({
                'success': True,
                'topic': {
                    'id': str(topic.id),
                    'board': topic.board,
                    'year': topic.year_level,
                    'subject': topic.subject,
                    'topic': topic.topic,
                    'subtopic': topic.subtopic,
                    'status': topic.status,
                    'lastUpdated': topic.last_updated.isoformat(),
                    'coveredBy': topic.covered_by
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'error': 'POST required'}, status=400)

def generate_worksheet_bytes(file_name, topic, year, subject):
    """
    Generates and returns the bytes of a real, gorgeous, 4J branded certified classroom worksheet
    in PDF, DOCX, or PPTX format matching the selected topic, subject, and year.
    """
    ext = file_name.split('.')[-1].lower() if '.' in file_name else 'pdf'
    buffer = io.BytesIO()
    
    if ext == 'pdf':
        can = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        gold_color = HexColor("#927116")
        dark_grey = HexColor("#111827")
        light_grey = HexColor("#4b5563")
        
        # 1. Header Line & Title
        can.setFillColor(gold_color)
        can.setStrokeColor(gold_color)
        can.setFont("Times-Bold", 9)
        can.drawString(40, height - 35, "4J'S EDUCATIONAL ACADEMY — STRIVING FOR DISTINCTION")
        can.setLineWidth(0.75)
        can.line(40, height - 38, width - 40, height - 38)
        
        # 2. Large Royal Crown Watermark in Center
        can.saveState()
        can.setFillAlpha(0.035)
        can.setStrokeAlpha(0.035)
        cx = width / 2
        cy = height / 2
        
        path = can.beginPath()
        path.moveTo(cx - 70, cy - 25)
        path.lineTo(cx - 70, cy + 30)
        path.lineTo(cx - 35, cy + 5)
        path.lineTo(cx, cy + 45)
        path.lineTo(cx + 35, cy + 5)
        path.lineTo(cx + 70, cy + 30)
        path.lineTo(cx + 70, cy - 25)
        path.close()
        can.drawPath(path, fill=True, stroke=True)
        can.arc(cx - 90, cy - 50, cx + 90, cy + 50, 180, 180)
        can.restoreState()
        
        # 3. Document Title block
        can.setFillColor(dark_grey)
        can.setFont("Times-Bold", 18)
        can.drawString(40, height - 80, f"{year} Certified Classroom Worksheet")
        
        can.setFont("Times-Italic", 12)
        can.setFillColor(gold_color)
        can.drawString(40, height - 100, f"Subject: {subject} — UK Mapped Curriculum Standards")
        
        can.setLineWidth(0.5)
        can.setStrokeColor(HexColor("#e5e7eb"))
        can.line(40, height - 115, width - 40, height - 115)
        
        # 4. Focus Theme & Metadata block
        can.setFillColor(dark_grey)
        can.setFont("Times-Bold", 11)
        can.drawString(40, height - 140, "FOCUS THEME / TOPIC STUDY:")
        
        can.setFont("Times-Roman", 11)
        can.setFillColor(HexColor("#1e3a8a"))
        can.drawString(220, height - 140, f"{topic}")
        
        can.setFillColor(dark_grey)
        can.setFont("Times-Bold", 10)
        can.drawString(40, height - 165, "STUDENT NAME:")
        can.setStrokeColor(HexColor("#9ca3af"))
        can.line(140, height - 168, 320, height - 168)
        
        can.drawString(340, height - 165, "DATE:")
        can.line(390, height - 168, 500, height - 168)
        
        # 5. Core Syllabus Questions
        can.setFillColor(gold_color)
        can.setFont("Times-Bold", 12)
        can.drawString(40, height - 210, "SECTION A: FUNDAMENTAL CORE EXERCISES")
        
        can.setFillColor(dark_grey)
        can.setFont("Times-Roman", 10)
        y_offset = height - 240
        
        questions = [
            f"1. conceptual review: Explain the primary mathematical or structural rules governing '{topic}' within this academic level.",
            "   Provide three rigorous mathematical examples illustrating how to solve these problems standardly.",
            f"2. core challenge: Formulate and solve the following structured curriculum question relating to '{topic}':",
            "   [Show all working steps clearly, detailing variables, constants, and formula derivations on your page.]",
            "3. diagnostic checklist: What are the two most common errors students commit when working through these concepts?",
            "   How does a tuition HOD standardly advise avoiding these common analytical pitfalls?"
        ]
        
        for q in questions:
            can.drawString(40, y_offset, q)
            y_offset -= 20
            
        y_offset -= 10
        can.setFillColor(gold_color)
        can.setFont("Times-Bold", 12)
        can.drawString(40, y_offset, "SECTION B: SYLLABUS APPLICATION PROBLEMS")
        y_offset -= 30
        
        can.setFillColor(dark_grey)
        can.setFont("Times-Roman", 10)
        app_questions = [
            f"4. word problem challenge: A standard curriculum case scenario applies '{topic}' constraints directly.",
            "   Derive a formula to optimize the variables under Edexcel curriculum guidelines.",
            f"5. examination style review: Solve the following GCSE/A-Level mock paper style query for '{topic}':",
            "   'Calculate the resultant variables given initial conditions. Express your answer to 3 significant figures.'"
        ]
        
        for q in app_questions:
            can.drawString(40, y_offset, q)
            y_offset -= 20
        
        # 6. Page Footer margin
        can.setFillColor(light_grey)
        can.setFont("Times-Italic", 8)
        can.drawString(40, 25, "Certified Classroom Worksheet — 4J's Educational Academy Ltd")
        can.drawRightString(width - 40, 25, "Page 1 of 1 (Curriculum Standard Copy)")
        
        can.save()
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes, 'application/pdf'
        
    elif ext == 'docx':
        doc = docx.Document()
        
        # Add Branded header
        p_head = doc.add_paragraph()
        run_h = p_head.add_run("4J'S EDUCATIONAL ACADEMY — STRIVING FOR DISTINCTION")
        run_h.font.bold = True
        run_h.font.name = 'Times New Roman'
        run_h.font.color.rgb = docx.shared.RGBColor(146, 113, 22) # Gold RGB
        
        doc.add_heading(f"{year} - {subject} Certified Worksheet", level=1)
        doc.add_paragraph(f"Focus Topic: {topic}")
        doc.add_paragraph("Syllabus Standards: Mapped for GCSE & Edexcel Curriculum Guidelines")
        
        doc.add_heading("Section A: Theoretical Foundations", level=2)
        doc.add_paragraph(f"1. Detail the conceptual definitions and formulas that form the basis of '{topic}'.")
        doc.add_paragraph("2. Illustrate two detailed numerical examples showcasing complete step-by-step solutions.")
        
        doc.add_heading("Section B: Curriculum Exercise Questions", level=2)
        doc.add_paragraph(f"3. Core Question: Solve a standard GCSE-level problem utilizing '{topic}' models.")
        doc.add_paragraph("4. Extended Question: Discuss how these principles are applied in advanced mechanics or statistical models.")
        
        doc.save(buffer)
        docx_bytes = buffer.getvalue()
        buffer.close()
        return docx_bytes, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        
    elif ext == 'pptx':
        prs = Presentation()
        
        slide_layout = prs.slide_layouts[5] # Blank with title
        slide = prs.slides.add_slide(slide_layout)
        
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(1), Inches(9), Inches(2))
        tf = title_box.text_frame
        p = tf.add_paragraph()
        p.text = "4J'S EDUCATIONAL ACADEMY"
        p.font.bold = True
        p.font.size = Pt(36)
        p.font.color.rgb = pptx.dml.color.RGBColor(146, 113, 22)
        
        p2 = tf.add_paragraph()
        p2.text = f"{year} {subject} Seminar: {topic}"
        p2.font.size = Pt(20)
        
        slide2 = prs.slides.add_slide(prs.slide_layouts[5])
        title_box2 = slide2.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(1))
        title_box2.text_frame.text = f"Learning Objectives: {topic}"
        
        content_box2 = slide2.shapes.add_textbox(Inches(0.5), Inches(1.8), Inches(9), Inches(4))
        tf2 = content_box2.text_frame
        tf2.add_paragraph().text = f"- Define and explain core concepts of {topic}."
        tf2.add_paragraph().text = "- Apply standard algebraic or structural formulas to derive correct values."
        tf2.add_paragraph().text = "- Review and analyze common errors in Edexcel examination papers."
        
        prs.save(buffer)
        pptx_bytes = buffer.getvalue()
        buffer.close()
        return pptx_bytes, 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        
    return b"", "application/octet-stream"

def api_download_worksheet(request):
    """
    Downloads a real, gorgeous, 4J branded certified classroom worksheet using the helper generator.
    """
    file_name = request.GET.get('fileName', 'Worksheet.pdf')
    topic = request.GET.get('topic', 'General Revision')
    year = request.GET.get('year', 'Year Level')
    subject = request.GET.get('subject', 'Maths')
    
    data, content_type = generate_worksheet_bytes(file_name, topic, year, subject)
    
    response = HttpResponse(data, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response

def api_download_all_zip(request):
    """
    Generates and downloads a real in-memory ZIP archive bundling all matching certified resource worksheets.
    """
    query = request.GET.get('query', '').lower()
    year_filter = request.GET.get('year', 'All')
    subj_filter = request.GET.get('subject', 'All')
    topic_filter = request.GET.get('topic', '')
    
    # Filter database resource entries exactly matching front-end criteria
    queryset = ResourceItem.objects.all()
    filtered_resources = []
    
    for r in queryset:
        # Match Year
        if year_filter != 'All' and r.year != year_filter:
            continue
            
        # Match Subject (case-insensitive with mechanics fallback)
        if subj_filter != 'All':
            subj_match = False
            if r.subject == subj_filter:
                subj_match = True
            elif subj_filter.lower() in r.subject.lower():
                subj_match = True
            elif subj_filter.lower() == 'mechanics' and 'mechanic' in r.subject.lower():
                subj_match = True
            if not subj_match:
                continue
                
        # Match Topic
        if topic_filter and r.topic.strip() != topic_filter.strip():
            continue
            
        # Match Search Query
        if query:
            query_match = (
                query in r.file_name.lower() or
                query in r.topic.lower() or
                query in r.subject.lower()
            )
            if not query_match:
                continue
                
        filtered_resources.append(r)
        
    if not filtered_resources:
        return HttpResponse("No resources found matching the specified filters.", status=404)
        
    # Compile matching files into in-memory ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for r in filtered_resources:
            file_data, _ = generate_worksheet_bytes(r.file_name, r.topic, r.year, r.subject)
            zip_file.writestr(r.file_name, file_data)
            
    zip_data = zip_buffer.getvalue()
    zip_buffer.close()
    
    response = HttpResponse(zip_data, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="4j_educational_worksheets_collection.zip"'
    return response

