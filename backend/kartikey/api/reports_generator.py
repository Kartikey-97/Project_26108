import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

def generate_pdf_report(analysis_data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.textColor = colors.HexColor('#0f766e')
    h2_style = styles['Heading2']
    h2_style.textColor = colors.HexColor('#1f2937')
    normal_style = styles['Normal']
    
    elements = []
    
    # Title
    elements.append(Paragraph("StandIQ Technical Procurement Report", title_style))
    elements.append(Spacer(1, 10))
    
    # Meta Info
    metadata = [
        ["Analysis Title:", analysis_data.get('tender_title', 'Untitled Analysis')],
        ["Generated At:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["Overall Status:", analysis_data.get('status', 'Unknown').upper()],
    ]
    meta_table = Table(metadata, colWidths=[100, 400])
    meta_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#374151')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 20))
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", h2_style))
    elements.append(Spacer(1, 5))
    summary_text = analysis_data.get('summary', 'No summary available.')
    elements.append(Paragraph(summary_text, normal_style))
    elements.append(Spacer(1, 20))
    
    # Applicable Standards
    elements.append(Paragraph("Applicable Indian Standards", h2_style))
    elements.append(Spacer(1, 5))
    
    standards = analysis_data.get('standards', [])
    if standards:
        std_data = [["Standard Code", "Title", "Status"]]
        for s in standards:
            std_data.append([
                s.get('designation') or s.get('id', ''),
                Paragraph(s.get('title', ''), normal_style),
                s.get('status', 'active')
            ])
        std_table = Table(std_data, colWidths=[100, 320, 80])
        std_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#ccfbf1')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#115e59')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(std_table)
    else:
        elements.append(Paragraph("No standards matched.", normal_style))
        
    elements.append(Spacer(1, 20))
    
    # Requirements / Findings
    elements.append(Paragraph("Compliance Findings", h2_style))
    elements.append(Spacer(1, 5))
    
    findings = analysis_data.get('findings', [])
    if findings:
        find_data = [["Finding", "Status", "Reason"]]
        for f in findings:
            find_data.append([
                Paragraph(f.get('verdict', '').replace('_', ' ').title(), normal_style),
                f.get('status', 'Reviewed'),
                Paragraph(f.get('reason', ''), normal_style)
            ])
        find_table = Table(find_data, colWidths=[120, 80, 300])
        find_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#1f2937')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(find_table)
    else:
        elements.append(Paragraph("No findings generated.", normal_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
