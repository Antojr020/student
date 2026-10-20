import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generate_marksheet_pdf(student, marks, sgpa, cgpa, exam_name=None, academic_year=None):
    """
    Generate an enterprise-grade, publication-quality official Marksheet PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CollegeTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0f2b5c')
    )
    
    subtitle_style = ParagraphStyle(
        'CollegeSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#475569')
    )

    doc_header_style = ParagraphStyle(
        'DocHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e3a8a')
    )

    label_style = ParagraphStyle(
        'InfoLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#1e293b')
    )

    val_style = ParagraphStyle(
        'InfoVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#334155')
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1e293b')
    )

    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e293b')
    )

    # 1. Header Banner
    story.append(Paragraph("SMARTMARK INSTITUTE OF TECHNOLOGY & SCIENCE", title_style))
    story.append(Paragraph("Autonomous Institution &bull; Approved by AICTE &bull; Accredited 'A++' by NAAC &bull; Affiliated to University", subtitle_style))
    story.append(Paragraph("College Campus Road, Technology Corridor &bull; Tel: +91 44 2345 6789 &bull; Web: www.smartmark.edu", subtitle_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0f2b5c'), spaceBefore=2, spaceAfter=6))
    
    exam_str = f" - {exam_name}" if exam_name else ""
    story.append(Paragraph(f"OFFICIAL GRADE STATEMENT &bull; SEMESTER {student.current_semester}{exam_str}", doc_header_style))
    story.append(Spacer(1, 8))

    # 2. Student Particulars Card
    ay_str = academic_year or "2025-2026"
    dept_str = student.department if hasattr(student, 'department') else "Computer Science"
    prog_str = student.programme if hasattr(student, 'programme') else "B.Tech"

    info_data = [
        [
            Paragraph("<b>Student Name:</b>", label_style),
            Paragraph(student.name.upper(), val_style),
            Paragraph("<b>Registration No:</b>", label_style),
            Paragraph(f"<b>{student.register_no}</b>", val_style)
        ],
        [
            Paragraph("<b>Department:</b>", label_style),
            Paragraph(dept_str, val_style),
            Paragraph("<b>Degree / Course:</b>", label_style),
            Paragraph(prog_str, val_style)
        ],
        [
            Paragraph("<b>Current Semester:</b>", label_style),
            Paragraph(f"Semester {student.current_semester}", val_style),
            Paragraph("<b>Academic Year:</b>", label_style),
            Paragraph(ay_str, val_style)
        ],
        [
            Paragraph("<b>Date of Issue:</b>", label_style),
            Paragraph(datetime.now().strftime("%d-%b-%Y"), val_style),
            Paragraph("<b>Enrollment Status:</b>", label_style),
            Paragraph(getattr(student, 'enrollment_status', 'Active'), val_style)
        ]
    ]

    info_table = Table(info_data, colWidths=[85, 175, 100, 160])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 10))

    # 3. Marks Data Table
    table_headers = [
        Paragraph("<b>#</b>", table_header_style),
        Paragraph("<b>Code</b>", table_header_style),
        Paragraph("<b>Subject Name</b>", table_header_style),
        Paragraph("<b>Credits</b>", table_header_style),
        Paragraph("<b>Internal<br/>(40)</b>", table_header_style),
        Paragraph("<b>External<br/>(60)</b>", table_header_style),
        Paragraph("<b>Total<br/>(100)</b>", table_header_style),
        Paragraph("<b>Grade</b>", table_header_style),
        Paragraph("<b>Points</b>", table_header_style),
        Paragraph("<b>Result</b>", table_header_style)
    ]

    marks_data = [table_headers]
    total_credits = 0
    earned_credits = 0

    for idx, m in enumerate(marks, start=1):
        subj = m.subject
        c = subj.credits if subj else 3
        total_credits += c
        if m.result == 'PASS':
            earned_credits += c

        internal_tot = m.internal_marks + m.assignment_marks + m.practical_marks
        
        result_color = '#15803d' if m.result == 'PASS' else '#b91c1c'
        result_p = Paragraph(f"<font color='{result_color}'><b>{m.result}</b></font>", table_cell_center)

        marks_data.append([
            Paragraph(str(idx), table_cell_center),
            Paragraph(subj.subject_code if subj else "N/A", table_cell_center),
            Paragraph((subj.subject_name if subj else "Subject")[:35], table_cell_style),
            Paragraph(str(c), table_cell_center),
            Paragraph(f"{internal_tot:.1f}", table_cell_center),
            Paragraph(f"{m.external_marks:.1f}", table_cell_center),
            Paragraph(f"<b>{m.total_marks:.1f}</b>", table_cell_center),
            Paragraph(f"<b>{m.grade}</b>", table_cell_center),
            Paragraph(str(m.grade_point), table_cell_center),
            result_p
        ])

    marks_table = Table(marks_data, colWidths=[20, 55, 175, 40, 45, 45, 45, 35, 30, 45])
    marks_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f2b5c')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#0f2b5c')),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(marks_table)
    story.append(Spacer(1, 10))

    # 4. Academic Summary Card
    all_pass = all(m.result == 'PASS' for m in marks) if marks else False
    overall_status = "PASSED" if all_pass and len(marks) > 0 else ("RE-APPEAR REQUIRED" if len(marks) > 0 else "PENDING")
    status_color = "#15803d" if all_pass else "#b91c1c"

    summary_data = [
        [
            Paragraph("<b>Total Credits Registered:</b>", label_style),
            Paragraph(str(total_credits), val_style),
            Paragraph("<b>SGPA (Current Semester):</b>", label_style),
            Paragraph(f"<font color='#0f2b5c' size='10'><b>{sgpa:.2f}</b></font>", val_style)
        ],
        [
            Paragraph("<b>Credits Successfully Earned:</b>", label_style),
            Paragraph(str(earned_credits), val_style),
            Paragraph("<b>Cumulative CGPA:</b>", label_style),
            Paragraph(f"<font color='#0f2b5c' size='10'><b>{cgpa:.2f}</b></font>", val_style)
        ],
        [
            Paragraph("<b>Semester Result Status:</b>", label_style),
            Paragraph(f"<font color='{status_color}'><b>{overall_status}</b></font>", val_style),
            Paragraph("<b>Classification:</b>", label_style),
            Paragraph("First Class with Distinction" if cgpa >= 8.5 else ("First Class" if cgpa >= 6.5 else ("Second Class" if cgpa >= 5.0 else "Pass Class")), val_style)
        ]
    ]

    summary_table = Table(summary_data, colWidths=[140, 120, 140, 120])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 10))

    # 5. Grading Legend
    legend_text = (
        "<b>Grading System (10-Point Scale):</b> "
        "<b>O:</b> 90-100% (10 - Outstanding) | "
        "<b>A+:</b> 80-89% (9 - Excellent) | "
        "<b>A:</b> 70-79% (8 - Very Good) | "
        "<b>B+:</b> 60-69% (7 - Good) | "
        "<b>B:</b> 50-59% (6 - Above Average) | "
        "<b>C:</b> 40-49% (5 - Pass) | "
        "<b>RA:</b> &lt;40% (0 - Re-appear)"
    )
    story.append(Paragraph(legend_text, ParagraphStyle('Legend', parent=styles['Normal'], fontName='Helvetica', fontSize=6.5, leading=8.5, textColor=colors.HexColor('#64748b'), alignment=TA_CENTER)))
    story.append(Spacer(1, 24))

    # 6. Signatures Footer
    sig_data = [
        [
            Paragraph("Prepared & Verified By<br/><font size='6' color='#94a3b8'>Academic Section</font>", ParagraphStyle('Sig1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, alignment=TA_CENTER)),
            Paragraph("Controller of Examinations<br/><font size='6' color='#94a3b8'>SmartMark Academic Office</font>", ParagraphStyle('Sig2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, alignment=TA_CENTER)),
            Paragraph("Principal / Dean<br/><font size='6' color='#94a3b8'>College of Technology</font>", ParagraphStyle('Sig3', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, alignment=TA_CENTER))
        ]
    ]
    sig_table = Table(sig_data, colWidths=[170, 180, 170])
    sig_table.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 0.75, colors.HexColor('#94a3b8')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(sig_table)

    doc.build(story)
    buffer.seek(0)
    return buffer
