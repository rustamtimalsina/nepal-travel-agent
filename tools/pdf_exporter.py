import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

def generate_pdf_itinerary(title: str, markdown_content: str) -> bytes:
    """
    Parses agent itinerary markdown text and compiles it into clean PDF bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1B4D3E')
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2E5B88'),
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#222222')
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        bulletIndent=5,
        spaceAfter=2
    )

    story = []
    story.append(Paragraph(title, title_style))
    story.append(Paragraph("Nepal Himalayan Autonomous Trek Planner & Safety Briefing", styles['Italic']))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1B4D3E'), spaceAfter=10))

    # Strip emoji characters to prevent ReportLab encoding errors
    cleaned_md = re.sub(r'[^\x00-\x7F]+', '', markdown_content)

    for line in cleaned_md.split('\n'):
        text = line.strip()
        if not text:
            story.append(Spacer(1, 3))
            continue

        if text.startswith('# ') or text.startswith('## ') or text.startswith('### '):
            header_text = text.lstrip('#').strip()
            story.append(Paragraph(f"<b>{header_text}</b>", h1_style))
        elif text.startswith('- [ ]') or text.startswith('* ') or text.startswith('- '):
            clean_item = re.sub(r'^[-*](\s*\[\s*\])?\s*', '', text)
            clean_item = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean_item)
            story.append(Paragraph(f"&bull; {clean_item}", bullet_style))
        else:
            bolded_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            story.append(Paragraph(bolded_text, body_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes