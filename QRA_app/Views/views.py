from ..models import *
from QRA_app.permission import *
from django.db import connections
from django.shortcuts import render
from django.http import HttpResponse
from django.db.utils import OperationalError
from django.utils.connection import ConnectionDoesNotExist


# Datacbase connection check
def db_check():
    try:
        connections["default"].ensure_connection()
    except (OperationalError, ConnectionDoesNotExist):
        return HttpResponse("<h1>Database is not connected!</h1>", status=500)
    return None


@superuser_required
def superuser_dashboard(request):
    courses = CourseModel.objects.select_related("department").all()
    assignments = CourseAssignment.objects.select_related("course", "teacher").all()
    departments = DepartmentModel.objects.all()
    teachers = User.objects.filter(role='teacher')
    students = User.objects.filter(role='student')

    dashboard_cards = [
        {
            "label": "Teachers",
            "icon": "bi-person-badge",
            "value": teachers.count(),
            "bg": "rgba(16, 44, 78, 0.1)",
        },
        {
            "label": "Students",
            "icon": "bi-people",
            "value": students.count(),
            "bg": "rgba(43, 178, 162, 0.1)",
        },
        {
            "label": "Courses",
            "icon": "bi-journal-check",
            "value": courses.count(),
            "bg": "rgba(16, 44, 78, 0.1)",
        },
        {
            "label": "Active Assignments",
            "icon": "bi-check2-square",
            "value": assignments.count(),
            "bg": "rgba(43, 178, 162, 0.1)",
        },
        {
            "label": "Departments",
            "icon": "bi-diagram-3",
            "value": departments.count(),
            "bg": "rgba(16, 44, 78, 0.1)",
        },
    ]

    context = {
        "dashboard_cards": dashboard_cards,
        "courses": courses,
        "assignments": assignments,
        "departments": departments,
        "teachers":teachers,
        "students":students,
    }
    return render(request, "UI/superadmin/dashboard.html", context)

@superuser_required
def home(request):
    try:
        db_response = db_check()
        if db_response:
            return db_response
    except Exception as e:
        return HttpResponse(f"<h1>Error: {str(e)}</h1>", status=500)

    return render(request, "home.html")
