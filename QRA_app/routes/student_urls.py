from django.urls import path
from QRA_app.Views import students_views

urlpatterns = [
    path(
        "student/dashboard/", students_views.student_dashboard, name="student_dashboard"
    ),
    path(
        "student/attendance/submit/", students_views.submit_attendance, name="submit_attendance"
    ),
    path(
        "student/attendance/history/",
        students_views.attendance_history,
        name="attendance_history",
    ),
    path(
        "student/profile/", students_views.student_profile, name="student_profile")
]
