import html
from io import BytesIO
from xml.sax.saxutils import escape as xml_escape
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def clean_text(s) -> str:
    if s is None:
        return ""
    return xml_escape(str(s))

def generate_pdf_report(investigation_data: dict) -> bytes:
    """
    Generates a publication-grade PDF investigation report using ReportLab.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom editorial styles
    header_style = ParagraphStyle(
        'DocHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1B3B2B')
    )
    
    subhead_style = ParagraphStyle(
        'DocSubhead',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4A5450')
    )

    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1A1E1C'),
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#232826')
    )

    status_color = colors.HexColor('#1B7A43')
    raw_status = investigation_data.get('verdict_category') or investigation_data.get('assessment_status') or 'INSUFFICIENT EVIDENCE'
    status_text = raw_status.upper()
    if 'CONTRADICTED' in status_text or 'MANIPULATION' in status_text or 'AI-GENERATED' in status_text:
        status_color = colors.HexColor('#9B2C2C')
    elif 'INSUFFICIENT' in status_text or 'INCONCLUSIVE' in status_text:
        status_color = colors.HexColor('#C97A1E')

    badge_style = ParagraphStyle(
        'StatusBadge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=status_color
    )

    story = []

    # Title Banner
    story.append(Paragraph("TRUTHLENS &bull; INVESTIGATION DOSSIER", subhead_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Dossier ID: {clean_text(investigation_data.get('id', 'N/A'))}", header_style))
    story.append(Paragraph(f"Conducted: {clean_text(investigation_data.get('created_at', ''))} | Mode: {clean_text(investigation_data.get('mode', 'deep')).upper()}", subhead_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1B3B2B'), spaceAfter=12))

    # Executive Verdict
    story.append(Paragraph("EXECUTIVE VERDICT", h2_style))
    story.append(Paragraph(f"Status: {clean_text(status_text)} &bull; {clean_text(investigation_data.get('verdict_headline', ''))}", badge_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Summary:</b> {clean_text(investigation_data.get('summary', 'No summary available.'))}", body_style))
    story.append(Spacer(1, 10))

    # Claim Decomposition Table
    claim_bd = investigation_data.get('claim_breakdown') or {}
    claim_table_data = [
        [Paragraph("<b>Original Claim</b>", body_style), Paragraph(clean_text(investigation_data.get('original_claim', '')), body_style)],
        [Paragraph("<b>Decomposed Event</b>", body_style), Paragraph(clean_text(claim_bd.get('event', 'Unspecified')), body_style)],
        [Paragraph("<b>Reported Location</b>", body_style), Paragraph(clean_text(claim_bd.get('location', 'Unspecified')), body_style)],
        [Paragraph("<b>Reported Time</b>", body_style), Paragraph(clean_text(claim_bd.get('time_reference', 'Unspecified')), body_style)],
    ]
    t_claim = Table(claim_table_data, colWidths=[130, 400])
    t_claim.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FBF9F5')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E6E1D8')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_claim)
    story.append(Spacer(1, 12))

    # Image Forensics, AI Vision Description & Metadata
    img_an = investigation_data.get('image_analysis') or {}
    scene_clues = img_an.get('scene_clues') or {}
    ai_desc = scene_clues.get('image_description') or 'Visual forensic description unavailable.'
    v_model = scene_clues.get('vision_model_used') or 'Local Forensic Vision Engine'

    story.append(Paragraph("AI-GENERATED VISUAL OBSERVATIONS", h2_style))
    story.append(Paragraph(f"<b>Vision Model:</b> {v_model}", subhead_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph(f"<b>Visual Description:</b> {ai_desc}", body_style))
    
    vis_objs = scene_clues.get('visible_objects', [])
    if vis_objs:
        story.append(Spacer(1, 2))
        story.append(Paragraph(f"<b>Visible Objects / Scene:</b> {', '.join(vis_objs[:8])}", body_style))

    vis_uncert = scene_clues.get('visual_uncertainties', [])
    if vis_uncert:
        story.append(Spacer(1, 2))
        story.append(Paragraph(f"<b>Visual Limitations:</b> {'; '.join(vis_uncert[:3])}", subhead_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("IMAGE FORENSICS & METADATA", h2_style))
    meta_table_data = [
        [
            Paragraph(f"<b>Format:</b> {img_an.get('file_type', 'N/A')}", body_style),
            Paragraph(f"<b>Dimensions:</b> {img_an.get('dimensions', 'N/A')}", body_style),
            Paragraph(f"<b>Perceptual Hash:</b> {str(img_an.get('perceptual_hash', 'N/A'))[:16]}...", body_style)
        ],
        [
            Paragraph(f"<b>Camera/Device:</b> {str(img_an.get('exif_data', {}).get('Model', 'None / Stripped'))}", body_style),
            Paragraph(f"<b>Capture Date:</b> {str(img_an.get('exif_data', {}).get('DateTimeOriginal', 'Not available in EXIF'))}", body_style),
            Paragraph(f"<b>GPS Coordinates:</b> {img_an.get('gps_data', {}).get('redacted_display', 'No GPS tags')}", body_style)
        ]
    ]
    t_meta = Table(meta_table_data, colWidths=[175, 175, 180])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F4F1EA')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D9D3C7')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 12))

    # Retrieved Grounded Evidence Items
    story.append(Paragraph("RETRIEVED GROUNDED EVIDENCE & CORROBORATION", h2_style))
    evidence_items = investigation_data.get('evidence_items', [])
    if evidence_items:
        ev_rows = [
            [
                Paragraph("<b>Publisher / Source</b>", body_style),
                Paragraph("<b>Relationship</b>", body_style),
                Paragraph("<b>Reliability</b>", body_style),
                Paragraph("<b>Documented Passage Excerpt</b>", body_style)
            ]
        ]
        for ev in evidence_items[:5]:
            ev_rows.append([
                Paragraph(f"<b>{ev.get('publisher')}</b><br/><i>{ev.get('source_title', '')[:40]}...</i>", body_style),
                Paragraph(f"{ev.get('relationship_to_claim', '').upper()}", body_style),
                Paragraph(f"{int(ev.get('reliability_score', 0)*100)}%", body_style),
                Paragraph(f"{ev.get('passage', '')[:160]}...", body_style)
            ])
        t_ev = Table(ev_rows, colWidths=[120, 80, 60, 270])
        t_ev.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1B3B2B')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E6E1D8')),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_ev)
    else:
        story.append(Paragraph("No matching evidence records survived threshold filtering.", body_style))

    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#D9D3C7'), spaceAfter=8))
    
    # Responsible AI Disclaimer
    disclaimer_text = (
        "<b>Responsible AI Notice:</b> TRUTHLENS is an academic and investigative research platform. "
        "Evaluations are synthesized from available reference archives and computer vision signals. "
        "Absence of evidence is not proof of falsehood. Independent ground verification is recommended."
    )
    story.append(Paragraph(disclaimer_text, subhead_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
