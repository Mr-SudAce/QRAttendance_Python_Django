from django.http import JsonResponse
from ..QR_generator import generate_qr_base64
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from QRA_app.permission import student_required
from ..models import AttendanceSessionModel, EnrollmentModel, AttendanceRecordModel

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
    if not EnrollmentModel.objects.filter(student=student, course=session.course).exists():
        messages.error(request, "You are not enrolled in this course. Contact your teacher.")
        return redirect("student_dashboard")
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

def is_mobile(request):
    ua = request.META.get("HTTP_USER_AGENT", "").lower()
    return any(k in ua for k in ["mobi", "android", "iphone", "ipad"])

@student_required
def student_dashboard(request):
    mobile = is_mobile(request)
    context = {"is_mobile": mobile}

    if not mobile:
        student_courses = EnrollmentModel.objects.filter(
            student=request.user
        ).values_list("course_id", flat=True)

        session = (
            AttendanceSessionModel.objects.filter(
                course_id__in=student_courses,
                is_active=True,
                expires_at__gt=timezone.now(),
            )
            .order_by("-created_at")
            .first()
        )

        if session:
            context["session"] = session
            context["qr_code"] = generate_qr_base64(
                request.build_absolute_uri(session.qr_url)
            )

    return render(request, "UI/student/student_dashboard.html", context)

@student_required
def session_status(request, session_id):
    marked = AttendanceRecordModel.objects.filter(
        student=request.user, attendance_session_id=session_id
    ).exists()
    return JsonResponse({"marked": marked})


@student_required
def student_profile(request):
    student = request.user
    return render(request, "UI/student/student_profile.html", {"student": student})


@student_required
def attendance_history(request):
    attendance = AttendanceRecordModel.objects.filter(student=request.user)
    return render(
        request, "UI/student/attendance_history.html", {"attendance": attendance}
    )
