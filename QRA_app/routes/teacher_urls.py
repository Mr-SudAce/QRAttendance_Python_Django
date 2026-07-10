from django.urls import path
from QRA_app.Views import teachers_views

urlpatterns = [
    path(
        "teacher/dashboard/", teachers_views.teacher_dashboard, name="teacher_dashboard"
    ),
    path(
        "teacher/profile/",
        teachers_views.teacher_profile,
        name="teacher_profile",
    ),
    path(
        "teacher/sessions/create/<int:course_id>/",
        teachers_views.teacher_create_session,
        name="create_session",
    ),
    path(
        "teacher/sessions/close/<int:session_id>/",
        teachers_views.close_session,
        name="close_session",
    ),
    path(
        "teacher/attendance/history/",
        teachers_views.attendance_history_course,
        name="attendance_history_course",
    ),
]
