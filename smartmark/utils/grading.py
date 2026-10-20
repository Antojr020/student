def calculate_grade_and_points(total_marks, max_marks=100.0):
    """
    Calculate Letter Grade, Grade Points (10-point scale), and Pass/Fail result.
    Based on standard university / college credit system.
    """
    if max_marks <= 0:
        max_marks = 100.0
    percentage = (float(total_marks) / float(max_marks)) * 100.0

    if percentage >= 90:
        return 'O', 10, 'PASS'
    elif percentage >= 80:
        return 'A+', 9, 'PASS'
    elif percentage >= 70:
        return 'A', 8, 'PASS'
    elif percentage >= 60:
        return 'B+', 7, 'PASS'
    elif percentage >= 50:
        return 'B', 6, 'PASS'
    elif percentage >= 40:
        return 'C', 5, 'PASS'
    else:
        return 'RA', 0, 'FAIL' # Re-Appear (Fail)


def calculate_sgpa(marks_records):
    """
    Calculate Semester Grade Point Average (SGPA).
    SGPA = Sum(Course Credits * Grade Points) / Sum(Course Credits)
    """
    total_credit_points = 0.0
    total_credits = 0.0

    for mark in marks_records:
        if not mark.subject:
            continue
        credits = mark.subject.credits or 3
        points = mark.grade_point if mark.grade_point is not None else 0
        total_credit_points += (credits * points)
        total_credits += credits

    if total_credits == 0:
        return 0.0
    return round(total_credit_points / total_credits, 2)


def calculate_cgpa(student):
    """
    Calculate Cumulative Grade Point Average (CGPA) for a student across all completed subjects.
    Only considers approved/published marks if filter exists.
    """
    marks = student.marks.filter_by(status='approved').all() if hasattr(student.marks, 'filter_by') else student.marks.all()
    if not marks:
        # Fallback to any marks if none are explicitly approved
        marks = student.marks.all()
    if not marks:
        return 0.0
    return calculate_sgpa(marks)


def calculate_performance_summary(marks_records):
    """
    Summarize a collection of marks records: total marks, max marks, percentage, pass count, fail count.
    """
    total_obtained = sum(m.total_marks for m in marks_records)
    total_max = sum((m.subject.max_marks or 100.0) for m in marks_records if m.subject)
    pass_count = sum(1 for m in marks_records if m.result == 'PASS')
    fail_count = sum(1 for m in marks_records if m.result != 'PASS')
    total_count = len(marks_records)

    percentage = round((total_obtained / total_max) * 100, 2) if total_max > 0 else 0.0
    pass_percentage = round((pass_count / total_count) * 100, 1) if total_count > 0 else 0.0

    return {
        'total_obtained': total_obtained,
        'total_max': total_max,
        'percentage': percentage,
        'total_count': total_count,
        'pass_count': pass_count,
        'fail_count': fail_count,
        'pass_percentage': pass_percentage,
        'overall_result': 'PASS' if fail_count == 0 and total_count > 0 else ('FAIL' if total_count > 0 else 'N/A')
    }
