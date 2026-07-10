from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from QRA_app.permission import student_required
from ..models import AttendanceSessionModel, EnrollmentModel, AttendanceRecordModel


@student_required
def student_dashboard(request):
    return render(request, "UI/student/student_dashboard.html")


@student_required
def student_profile(request):
    student = request.user
    return render(request, "UI/student/student_profile.html", {"student": student})


@student_required
def submit_attendance(request):
    if request.method != "POST":
        return HttpResponse("Invalid request", status=400)
    student = request.user
    token = request.POST.get("token")
    if not token:
        return HttpResponse("QR token missing", status=400)
    session = get_object_or_404(AttendanceSessionModel, session_token=token)
    if not session.is_active:
        return HttpResponse("Session closed", status=400)
    if timezone.now() > session.expires_at:
        return HttpResponse("QR expired", status=400)
    EnrollmentModel.objects.get_or_create(student=student, course=session.course)
    already_marked = AttendanceRecordModel.objects.filter(
        student=student, attendance_session=session
    ).exists()
    if already_marked:
        messages.error(request, "Attendance already marked for this session.")
        return redirect("student_dashboard")
    AttendanceRecordModel.objects.create(
        student=student,
        attendance_session=session,
        status="present",
    )
    messages.success(request, "Attendance marked successfully.")
    return redirect("student_dashboard")


@student_required
def attendance_history(request):
    attendance = AttendanceRecordModel.objects.filter(student=request.user)
    return render(
        request, "UI/student/attendance_history.html", {"attendance": attendance}
    )
