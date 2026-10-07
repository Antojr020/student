import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def generate_marksheet_pdf(student, marks, sgpa, cgpa):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2.0, height - 1*inch, "SMARTMARK COLLEGE OF TECHNOLOGY")
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2.0, height - 1.3*inch, "Official Mark Sheet")
    
    # Student Info
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, height - 2*inch, f"Name: {student.name}")
    c.drawString(1*inch, height - 2.2*inch, f"Register No: {student.register_no}")
    c.drawString(1*inch, height - 2.4*inch, f"Programme: {student.programme} ({student.department})")
    c.drawString(5*inch, height - 2*inch, f"Semester: {student.semester}")
    
    # Table Header
    y = height - 3*inch
    c.drawString(1*inch, y, "Subject Code")
    c.drawString(2.5*inch, y, "Subject Name")
    c.drawString(5*inch, y, "Credits")
    c.drawString(6*inch, y, "Grade")
    c.drawString(7*inch, y, "Result")
    
    c.line(1*inch, y - 5, width - 1*inch, y - 5)
    
    # Marks Data
    c.setFont("Helvetica", 10)
    y -= 25
    for m in marks:
        c.drawString(1*inch, y, m.subject.subject_code)
        c.drawString(2.5*inch, y, m.subject.subject_name[:25])
        c.drawString(5.1*inch, y, str(m.subject.credits))
        c.drawString(6.1*inch, y, m.grade)
        c.drawString(7*inch, y, m.result)
        y -= 20
        
    c.line(1*inch, y, width - 1*inch, y)
    
    # Summary
    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y, f"SGPA: {sgpa:.2f}")
    c.drawString(3*inch, y, f"CGPA: {cgpa:.2f}")
    
    # Signatures
    y -= 2*inch
    c.drawString(1*inch, y, "Faculty Signature")
    c.drawString(6*inch, y, "Principal")
    
    c.save()
    buffer.seek(0)
    return buffer
