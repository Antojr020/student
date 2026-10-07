def calculate_grade_and_points(total_marks):
    if total_marks >= 90: return 'A+', 10, 'PASS'
    elif total_marks >= 80: return 'A', 9, 'PASS'
    elif total_marks >= 70: return 'B+', 8, 'PASS'
    elif total_marks >= 60: return 'B', 7, 'PASS'
    elif total_marks >= 50: return 'C', 6, 'PASS'
    elif total_marks >= 40: return 'D', 5, 'PASS'
    else: return 'F', 0, 'FAIL'

def calculate_sgpa(marks_records):
    total_credit_points = 0
    total_credits = 0
    for mark in marks_records:
        credits = mark.subject.credits
        points = mark.grade_point
        total_credit_points += (credits * points)
        total_credits += credits
    
    if total_credits == 0:
        return 0.0
    return round(total_credit_points / total_credits, 2)

def calculate_cgpa(student):
    marks = student.marks.all()
    if not marks: return 0.0
    return calculate_sgpa(marks)
