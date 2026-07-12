import uuid
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponse
from ..models import *
from QRA_app.permission import *
from django.shortcuts import render, redirect, get_object_or_404
from QRA_main.settings import BASE_URL


@teacher_required
def teacher_dashboard(request):
    courses = CourseModel.objects.filter(courseassignment__teacher=request.user)
    return render(request, "UI/teacher/teacher_dashboard.html", {"courses": courses})


@teacher_required
def teacher_profile(request):
    teacher = request.user
    return render(request, "UI/teacher/teacher_profile.html", {"teacher": teacher})


@teacher_required
def teacher_create_session(request, course_id):
    try:
        course = get_object_or_404(CourseModel, id=course_id, courseassignment__teacher=request.user)
        
        session = AttendanceSessionModel.objects.create(
            course=course,
            session_name=f"Session - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            expires_at=timezone.now() + timedelta(minutes=15),
            is_active=True,
        )
        
        qr_url = f"{BASE_URL}/student/scan/{session.session_token}"
        return render(
            request,
            "UI/teacher/qr_session.html",
            {"session": session, "qr_data": qr_url},
        )
    except Exception as e:
        return render(request, "UI/error.html", {"error": str(e)})


@teacher_required
def close_session(request, session_id):
    session = get_object_or_404(AttendanceSessionModel, id=session_id, course__courseassignment__teacher=request.user)
    session.is_active = False
    session.save()
    return redirect("teacher_dashboard")





# course related teacher session attedance
@teacher_required
def attendance_history_course(request):
    teacher_courses = CourseModel.objects.filter(courseassignment__teacher=request.user)

    course_attendance = []

    for course in teacher_courses:
        # Group history by session for a clearer timeline
        sessions = AttendanceSessionModel.objects.filter(course=course).order_by("-created_at")
        
        session_history = []
        for session in sessions:
            present_records = AttendanceRecordModel.objects.filter(
                attendance_session=session, 
                status="present"
            ).select_related("student")
            
            session_history.append({
                "session": session,
                "present_count": present_records.count(),
                "present_students": [r.student for r in present_records]
            })
            
        course_attendance.append({
            "course": course,
            "session_history": session_history
        })

    return render(
        request,
        "UI/teacher/course_attendance_history.html",
        {
            "course_attendance": course_attendance
        }
    )

@teacher_required
def manage_roster(request, course_id):
    course = get_object_or_404(
        CourseModel, id=course_id, courseassignment__teacher=request.user
    )
    enrollments = EnrollmentModel.objects.filter(course=course).select_related("student")
    enrolled_ids = enrollments.values_list("student_id", flat=True)
    available_students = User.objects.filter(role="student").exclude(id__in=enrolled_ids)
    return render(
        request,
        "UI/teacher/manage_roster.html",
        {
            "course": course,
            "enrollments": enrollments,
            "available_students": available_students,
        },
    )


@teacher_required
def enroll_student(request, course_id):
    course = get_object_or_404(
        CourseModel, id=course_id, courseassignment__teacher=request.user
    )
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        student = get_object_or_404(User, id=student_id, role="student")
        EnrollmentModel.objects.get_or_create(student=student, course=course)
    return redirect("manage_roster", course_id=course.id)


@teacher_required
def remove_student(request, course_id, enrollment_id):
    course = get_object_or_404(
        CourseModel, id=course_id, courseassignment__teacher=request.user
    )
    enrollment = get_object_or_404(EnrollmentModel, id=enrollment_id, course=course)
    if request.method == "POST":
        enrollment.delete()
    return redirect("manage_roster", course_id=course.id)