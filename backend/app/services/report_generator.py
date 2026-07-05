import os
import logging
from datetime import datetime
from typing import List, Dict
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from app.models.analysis import Analysis

logger = logging.getLogger("recruitsafe")

def get_risk_color(category: str) -> colors.Color:
    cat = category.lower() if category else ""
    if "high" in cat:
        return colors.HexColor("#EF4444")  # Red
    elif "suspicious" in cat:
        return colors.HexColor("#F97316")  # Orange
    elif "manual" in cat or "review" in cat:
        return colors.HexColor("#3B82F6")  # Blue
    elif "verification" in cat:
        return colors.HexColor("#EAB308")  # Yellow
    else:
        return colors.HexColor("#10B981")  # Green

def format_status_cell(label: str, state: str, body_style: ParagraphStyle) -> List[Paragraph]:
    state_upper = state.upper()
    
    if state_upper in ["VERIFIED", "VALID", "REACHABLE", "VALID HTTPS", "FOUND"]:
        color = "#10B981"  # Green
    elif state_upper in ["PARTIALLY VERIFIED", "DETECTED BUT NOT VERIFIED", "VERIFICATION PENDING"]:
        color = "#EAB308"  # Yellow
    elif state_upper in ["INVALID", "UNREACHABLE", "NOT FOUND", "DISPOSABLE EMAIL"]:
        color = "#EF4444"  # Red
    else:
        color = "#64748B"  # Gray for Unknown
        
    return [
        Paragraph(f"<b>{label}:</b>", body_style),
        Paragraph(f"<font color='{color}'><b>{state}</b></font>", body_style)
    ]

def generate_pdf_report(analysis: Analysis, output_path: str) -> None:
    logger.info(f"Generating V2.2 PDF report for analysis {analysis.id} at: {output_path}")
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    primary_color = colors.HexColor("#4F46E5")   # Indigo
    dark_text = colors.HexColor("#1E293B")       # Dark Slate
    muted_text = colors.HexColor("#64748B")      # Muted Slate
    border_color = colors.HexColor("#E2E8F0")    # Border gray
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=muted_text,
        spaceAfter=12
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=dark_text,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=dark_text,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=dark_text,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=dark_text
    )

    story = []
    
    # --- Header Banner ---
    story.append(Paragraph("RecruitSafe Cybersecurity Audit Assessment", title_style))
    created_str = analysis.created_at.strftime("%B %d, %Y at %H:%M UTC")
    story.append(Paragraph(f"REPORT ID: {analysis.id}  |  VERIFIED PORTAL V2.2  |  GENERATED: {created_str}", subtitle_style))
    story.append(Spacer(1, 4))
    
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
            Paragraph("<b>Input Quality Score:</b>", body_style),
            Paragraph(f"<b>{analysis.input_quality_score or 100}/100</b>", body_style)
        ]
    ]
    score_table = Table(score_data, colWidths=[100, 160, 130, 140])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('BOX', (0,0), (-1,-1), 1.2, primary_color),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 8))

    # --- Risk Progress Bar ---
    trust_width = max(10, min(520, (trust / 100) * 530))
    remainder_width = 530 - trust_width
    meter_data = [["", ""]]
    meter_table = Table(meter_data, colWidths=[trust_width, remainder_width], rowHeights=[8])
    meter_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), risk_color),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(Paragraph("<b>Opportunity Legitimacy Trust Meter:</b>", body_style))
    story.append(meter_table)
    story.append(Spacer(1, 8))
    
    # --- Executive AI Summary ---
    story.append(Paragraph("Executive Summary", section_heading))
    summary_text = analysis.ai_summary or "No summary generated."
    story.append(Paragraph(summary_text, body_style))
    
    # --- AI-Rule Agreement Explanation ---
    story.append(Paragraph("AI-Rule Agreement Details", section_heading))
    agreement_text = getattr(analysis, "agreement_explanation", None)
    if not agreement_text:
        agreement_text = f"Consensus score evaluated at {agreement}%. Rule engine and AI classification are in alignment."
    story.append(Paragraph(agreement_text, body_style))

    # --- Hiring Workflow Intelligence (NEW) ---
    workflow = getattr(analysis, "hiring_workflow", None) or {}
    if workflow:
        story.append(Paragraph("Hiring Workflow Intelligence", section_heading))
        wf_type = workflow.get("type", "Good")
        wf_score = workflow.get("score", 100)
        wf_diagram = workflow.get("diagram", "Application")
        wf_expl = workflow.get("explanation", "Legitimate pipeline")
        wf_missing = ", ".join(workflow.get("missing_stages", [])) or "None"
        
        wf_color = "#10B981" if wf_type == "Good" else ("#EF4444" if wf_type == "Very Risky" else "#F97316")
        
        wf_data = [
            [
                Paragraph("<b>Workflow Score:</b>", body_style),
                Paragraph(f"<b>{wf_score}/100</b>", body_style),
                Paragraph("<b>Sequence Type:</b>", body_style),
                Paragraph(f"<font color='{wf_color}'><b>{wf_type}</b></font>", body_style)
            ],
            [
                Paragraph("<b>Workflow Diagram:</b>", body_style),
                Paragraph(f"<i>{wf_diagram}</i>", body_style),
                Paragraph("<b>Missing Expected:</b>", body_style),
                Paragraph(f"<font color='#EF4444'><b>{wf_missing}</b></font>", body_style)
            ]
        ]
        wf_table = Table(wf_data, colWidths=[100, 160, 130, 140])
        wf_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FAFAFA")),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
            ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#CBD5E1")),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(wf_table)
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>Workflow Details:</b> {wf_expl}", body_style))
        story.append(Spacer(1, 8))

    # --- Verification Status Panel ---
    story.append(Paragraph("Verification Status Footprint Panel", section_heading))
    v_status = getattr(analysis, "verification_status", None) or {}
    
    p_web = v_status.get("Website", "Unknown")
    p_email = v_status.get("Corporate Email", "Unknown")
    p_whois = v_status.get("WHOIS", "Unknown")
    p_dns = v_status.get("DNS", "Unknown")
    p_ssl = v_status.get("SSL", "Unknown")
    p_linkedin = v_status.get("LinkedIn", "Not Found")
    p_priv = v_status.get("Privacy Policy", "Not Found")
    p_terms = v_status.get("Terms", "Not Found")
    p_contact = v_status.get("Contact Page", "Not Found")
    p_careers = v_status.get("Careers Page", "Not Found")
    
    row1 = format_status_cell("Company Website", p_web, body_style) + format_status_cell("Corporate Email", p_email, body_style)
    row2 = format_status_cell("WHOIS Registry Check", p_whois, body_style) + format_status_cell("DNS Resolution", p_dns, body_style)
    row3 = format_status_cell("SSL Connection Check", p_ssl, body_style) + format_status_cell("LinkedIn Profile", p_linkedin, body_style)
    row4 = format_status_cell("Privacy Policy Page", p_priv, body_style) + format_status_cell("Terms Compliance", p_terms, body_style)
    row5 = format_status_cell("Careers Page Link", p_careers, body_style) + [Paragraph("<b>Domain Age:</b>", body_style), Paragraph(f"<b>{v_status.get('Domain Age', 'Unknown')}</b>", body_style)]
    
    panel_data = [row1, row2, row3, row4, row5]
    panel_table = Table(panel_data, colWidths=[130, 130, 140, 130])
    panel_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FAFAFA")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#CBD5E1")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(panel_table)
    story.append(Spacer(1, 8))

    # --- Grouped Evidence Sections ---
    evidence_list = getattr(analysis, "evidence", []) or []
    positive_findings = getattr(analysis, "positive_findings", []) or []
    
    positives = [item for item in positive_findings if item.get("evidence_type", "positive") == "positive"]
    negatives = [item for item in evidence_list if item.get("evidence_type", "negative") == "negative"]
    unknowns = [item for item in evidence_list if item.get("evidence_type", "unknown") == "unknown"]

    # 1. Verified Positive Evidence
    if positives:
        story.append(Paragraph("Verified Positive Findings", section_heading))
        pos_data = [
            [
                Paragraph("<b>Audit Signal</b>", table_header_style),
                Paragraph("<b>Rule ID</b>", table_header_style),
                Paragraph("<b>Source</b>", table_header_style),
                Paragraph("<b>Audit Details</b>", table_header_style)
            ]
        ]
        for item in positives:
            title = item.get("title") or "Positive Signal"
            rule_id = item.get("rule_id") or "POS_000"
            src = item.get("source") or "Rule Engine"
            desc = item.get("reason") or item.get("description") or ""
            pos_data.append([
                Paragraph(f"<b>{title}</b>", table_cell_style),
                Paragraph(rule_id, table_cell_style),
                Paragraph(src, table_cell_style),
                Paragraph(desc, table_cell_style)
            ])
            
        pos_table = Table(pos_data, colWidths=[120, 70, 100, 240])
        pos_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#10B981")),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ]))
        story.append(pos_table)
        story.append(Spacer(1, 6))

    # 2. Risk Indicators (Negative Findings)
    if negatives:
        story.append(Paragraph("Risk Indicators & Technical Anomalies", section_heading))
        neg_data = [
            [
                Paragraph("<b>Risk Factor</b>", table_header_style),
                Paragraph("<b>Rule ID / Source</b>", table_header_style),
                Paragraph("<b>Impact</b>", table_header_style),
                Paragraph("<b>Anomalies & matched text</b>", table_header_style)
            ]
        ]
        for item in negatives:
            title = item.get("title") or "Anomalous Signal"
            rule_id = item.get("rule_id") or "NEG_000"
            src = item.get("source") or "Rule Engine"
            score = item.get("score") or 0
            desc = item.get("reason") or item.get("description") or ""
            matched = item.get("matched_text") or ""
            
            full_desc = f"{desc}"
            if matched:
                full_desc += f"<br/><i>Matched: '{matched}'</i>"
                
            neg_data.append([
                Paragraph(f"<b>{title}</b>", table_cell_style),
                Paragraph(f"{rule_id}<br/>{src}", table_cell_style),
                Paragraph(f"<font color='#EF4444'><b>{score} pts</b></font>", table_cell_style),
                Paragraph(full_desc, table_cell_style)
            ])
            
        neg_table = Table(neg_data, colWidths=[120, 90, 60, 260])
        neg_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EF4444")),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ]))
        story.append(neg_table)
        story.append(Spacer(1, 6))

    # 3. Unknown Findings
    if unknowns:
        story.append(Paragraph("Unknown / Not Verifiable Parameters", section_heading))
        unk_data = [
            [
                Paragraph("<b>Unverified Area</b>", table_header_style),
                Paragraph("<b>Rule ID</b>", table_header_style),
                Paragraph("<b>Source</b>", table_header_style),
                Paragraph("<b>Verification Gap Details</b>", table_header_style)
            ]
        ]
        for item in unknowns:
            title = item.get("title") or "Unverified Area"
            rule_id = item.get("rule_id") or "UNK_000"
            src = item.get("source") or "Rule Engine"
            desc = item.get("reason") or item.get("description") or ""
            unk_data.append([
                Paragraph(f"<b>{title}</b>", table_cell_style),
                Paragraph(rule_id, table_cell_style),
                Paragraph(src, table_cell_style),
                Paragraph(desc, table_cell_style)
            ])
            
        unk_table = Table(unk_data, colWidths=[120, 70, 100, 240])
        unk_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#475569")),  # Slate header
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ]))
        story.append(unk_table)
        story.append(Spacer(1, 6))
    
    # --- Actionable Contextual Recommendations ---
    story.append(Paragraph("Actionable Security Recommendations", section_heading))
    if not analysis.recommendations:
        story.append(Paragraph("• Verify recruiter identity and official corporate details before releasing credentials.", bullet_style))
        story.append(Paragraph("• Do not send payments, training deposits, or setup fees to personal bank accounts.", bullet_style))
    else:
        for rec in analysis.recommendations:
            story.append(Paragraph(f"• {rec}", bullet_style))
            
    story.append(Spacer(1, 8))
    
    # --- Processing Metadata ---
    story.append(Paragraph("Processing Metadata", section_heading))
    metadata_text = f"Correlation ID: {analysis.id} | Input Type: {analysis.input_type.upper()} | OCR Executed: {analysis.ocr_performed} | Processing time: {analysis.processing_time_ms or 0}ms"
    story.append(Paragraph(metadata_text, subtitle_style))
    
    # --- Footer Disclaimer ---
    story.append(Paragraph("<i>Disclaimer: RecruitSafe provides algorithmic and AI-based cybersecurity analysis based on user-supplied parameters. It does not certify legal contracts or provide formal legal advice. Please verify corporate recruiters via official channels.</i>", subtitle_style))

    doc.build(story)
    logger.info(f"PDF report successfully created for analysis {analysis.id}")
