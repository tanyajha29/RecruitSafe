import os
import logging
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from app.models.analysis import Analysis

logger = logging.getLogger("recruitsafe")

def get_risk_color(category: str) -> colors.Color:
    """
    Returns the theme color corresponding to the risk category.
    """
    cat = category.lower() if category else ""
    if "high" in cat:
        return colors.HexColor("#EF4444")  # Red
    elif "suspicious" in cat:
        return colors.HexColor("#F97316")  # Orange
    elif "review" in cat:
        return colors.HexColor("#3B82F6")  # Blue for Review Required
    elif "verification" in cat:
        return colors.HexColor("#EAB308")  # Yellow
    else:
        return colors.HexColor("#10B981")  # Green

def generate_pdf_report(analysis: Analysis, output_path: str) -> None:
    """
    Generates an upgraded, professional, explainable PDF report for a job analysis scan.
    """
    logger.info(f"Generating V2.0 PDF report for analysis {analysis.id} at: {output_path}")
    
    # 1. Page template setup
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom Palette styling
    primary_color = colors.HexColor("#4F46E5")   # Indigo
    dark_text = colors.HexColor("#1E293B")       # Dark Slate
    muted_text = colors.HexColor("#64748B")      # Muted Slate
    border_color = colors.HexColor("#E2E8F0")    # Border gray
    
    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=primary_color,
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=muted_text,
        spaceAfter=15
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=dark_text,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=dark_text,
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=dark_text,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=11,
        textColor=colors.white
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=dark_text
    )

    story = []
    
    # --- Header Banner ---
    story.append(Paragraph("RecruitSafe Verification Report (V2.0)", title_style))
    created_str = analysis.created_at.strftime("%B %d, %Y at %H:%M UTC")
    story.append(Paragraph(f"REPORT ID: {analysis.id}  |  GENERATED: {created_str}", subtitle_style))
    story.append(Spacer(1, 5))
    
    # --- Dual Score Cards ---
    trust = analysis.trust_score if analysis.trust_score is not None else 0
    confidence = analysis.confidence_score if analysis.confidence_score is not None else 0
    agreement = analysis.agreement_score if analysis.agreement_score is not None else 100
    risk_color = get_risk_color(analysis.risk_category)
    
    score_data = [
        [
            Paragraph("<b>Verdict:</b>", body_style),
            Paragraph(f"<font color='{risk_color.hexval()}'><b>{analysis.risk_category or 'Processing'}</b></font>", body_style),
            Paragraph("<b>Confidence Score:</b>", body_style),
            Paragraph(f"<b>{confidence}/100</b>", body_style)
        ],
        [
            Paragraph("<b>Trust Score:</b>", body_style),
            Paragraph(f"<b>{trust}/100</b>", body_style),
            Paragraph("<b>AI-Rule Agreement:</b>", body_style),
            Paragraph(f"<b>{agreement}%</b>", body_style)
        ]
    ]
    score_table = Table(score_data, colWidths=[110, 150, 130, 140])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('BOX', (0,0), (-1,-1), 1, primary_color),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 10))

    # --- Risk Meter (Dynamic 1-Row Progress Bar Table) ---
    # Width constraint: total width = 530 points
    trust_width = max(10, min(520, (trust / 100) * 530))
    remainder_width = 530 - trust_width
    
    meter_data = [["", ""]]
    meter_table = Table(meter_data, colWidths=[trust_width, remainder_width], rowHeights=[10])
    meter_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), risk_color),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(Paragraph("<b>Trust Score Risk Meter:</b>", body_style))
    story.append(meter_table)
    story.append(Spacer(1, 10))
    
    # --- Executive AI Summary ---
    story.append(Paragraph("Executive Summary", section_heading))
    summary_text = analysis.ai_summary or "No summary generated."
    story.append(Paragraph(summary_text, body_style))
    
    # --- Detailed Risk Explanation ---
    story.append(Paragraph("Detailed Risk Explanation", section_heading))
    explanation_text = analysis.risk_explanation or "No explanation generated."
    story.append(Paragraph(explanation_text, body_style))

    # --- Contradictions & Missing Information Alerts ---
    if analysis.contradictions or analysis.missing_information:
        alerts_data = []
        if analysis.contradictions:
            contr_list = "<br/>".join([f"• {c}" for c in analysis.contradictions])
            alerts_data.append([Paragraph(f"<b>Detected Contradictions:</b><br/>{contr_list}", body_style)])
        if analysis.missing_information:
            miss_list = ", ".join(analysis.missing_information)
            alerts_data.append([Paragraph(f"<b>Missing Information:</b> {miss_list}", body_style)])
            
        alerts_table = Table(alerts_data, colWidths=[530])
        alerts_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFBEB")),  # Light warning amber
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#FCD34D")),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(alerts_table)
        story.append(Spacer(1, 10))

    # --- Positive Findings Section ---
    positives = getattr(analysis, "positive_findings", [])
    if positives:
        story.append(Paragraph("Positive Safety Signals & Trust Bonuses", section_heading))
        pos_data = [
            [
                Paragraph("<b>Safety Factor</b>", table_header_style),
                Paragraph("<b>Bonus</b>", table_header_style),
                Paragraph("<b>Verification Details</b>", table_header_style)
            ]
        ]
        for item in positives:
            title = item.get("title") or item.get("factor_name") or "Verified Indicator"
            score = item.get("score") or item.get("points_deducted") or 0
            desc = item.get("description") or ""
            pos_data.append([
                Paragraph(f"<b>{title}</b>", table_cell_style),
                Paragraph(f"<font color='#10B981'><b>+{score} pts</b></font>", table_cell_style),
                Paragraph(desc, table_cell_style)
            ])
            
        pos_table = Table(pos_data, colWidths=[140, 80, 310])
        pos_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#10B981")),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ]))
        story.append(pos_table)
        story.append(Spacer(1, 10))
    
    # --- Red Flags / Technical Evidence Section ---
    story.append(Paragraph("Risk Findings & Technical Evidence", section_heading))
    if not analysis.evidence:
        story.append(Paragraph("No rule violations or domain intelligence anomalies were triggered in this scan.", body_style))
    else:
        evidence_data = [
            [
                Paragraph("<b>Violation Factor</b>", table_header_style),
                Paragraph("<b>Severity</b>", table_header_style),
                Paragraph("<b>Evidence & matched text</b>", table_header_style)
            ]
        ]
        
        for item in analysis.evidence:
            severity_str = item.get('severity', 'medium').upper()
            title = item.get('title') or item.get('factor_name') or 'Flagged Indicator'
            score = item.get('score') or -item.get('points_deducted', 0)
            desc = item.get('description', '')
            matched = item.get('matched_text') or ''
            explanation = item.get('explanation') or ''
            
            sev_color = "#EF4444" if "HIGH" in severity_str else ("#F97316" if "MEDIUM" in severity_str else "#64748B")
            
            # Combine details
            full_desc = f"{desc}<br/><i>Matched: '{matched}'</i>"
            if explanation:
                full_desc += f"<br/><b>Reason:</b> {explanation}"
                
            evidence_data.append([
                Paragraph(f"<b>{title}</b>", table_cell_style),
                Paragraph(f"<font color='{sev_color}'><b>{severity_str} ({score} pts)</b></font>", table_cell_style),
                Paragraph(full_desc, table_cell_style)
            ])
            
        evidence_table = Table(evidence_data, colWidths=[130, 100, 300])
        evidence_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), primary_color),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ]))
        story.append(evidence_table)
        
    story.append(Spacer(1, 10))
    
    # --- Actionable Recommendations ---
    story.append(Paragraph("Actionable Safety Recommendations", section_heading))
    if not analysis.recommendations:
        story.append(Paragraph("• Verify recruiter identity and official corporate details before releasing credentials.", bullet_style))
        story.append(Paragraph("• Do not send payments, training deposits, or setup fees to personal bank accounts.", bullet_style))
    else:
        for rec in analysis.recommendations:
            story.append(Paragraph(f"• {rec}", bullet_style))
            
    story.append(Spacer(1, 15))
    
    # --- Processing Metadata ---
    story.append(Paragraph("Processing Metadata", section_heading))
    metadata_text = f"Correlation ID: {analysis.id} | Input Type: {analysis.input_type.upper()} | OCR Executed: {analysis.ocr_performed} | Processing time: {analysis.processing_time_ms or 0}ms"
    story.append(Paragraph(metadata_text, subtitle_style))
    
    # --- Footer Disclaimer ---
    story.append(Paragraph("<i>Disclaimer: RecruitSafe provides algorithmic and AI-based cybersecurity analysis based on user-supplied parameters. It does not certify legal contracts or provide formal legal advice. Please verify corporate recruiters via official channels.</i>", subtitle_style))

    # Build document
    doc.build(story)
    logger.info(f"PDF report successfully created for analysis {analysis.id}")
