from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from QRA_app.models import *
from QRA_app.permission import *
from django.template.loader import render_to_string
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.db import *


@teacher_or_superuser_required
def course_dashboard(request):
    courses = CourseModel.objects.select_related("department").all()
    assignments = CourseAssignment.objects.select_related("course", "teacher").all()
    departments = DepartmentModel.objects.all()
    

    context = {
        "courses": courses,
        "assignments": assignments,
        "departments": departments,
    }

    return render(request, "UI/course/course_dashboard.html", context)


@superuser_required
def add_course(request):
    try:
        if request.method == "POST":
            course_name = request.POST.get("course_name")
            course_code = request.POST.get("course_code")
            course_description = request.POST.get("course_description")
            department_id = request.POST.get("course_department")

            if not all([course_name, course_code, department_id]):
                messages.error(request, "Please fill in all required fields.")
                return render(request, "UI/course/addcourse.html")

            if CourseModel.objects.filter(code=course_code).exists():
                messages.error(request, "Course code already exists.")
                return redirect("course_dashboard")

            department = get_object_or_404(DepartmentModel, id=department_id)

            CourseModel.objects.create(
                name=course_name,
                code=course_code,
                description=course_description,
                department=department,
            )

            messages.success(request, "Course created successfully.")
            return redirect("course_dashboard")

        departments = DepartmentModel.objects.all()
        return render(request, "UI/course/addcourse.html", {"departments": departments})

    except DepartmentModel.DoesNotExist:
        return HttpResponse("Department not found.")

    except Exception as e:
        print(e)
        return HttpResponse(f"An error occurred while adding the course. {e}")


@teacher_or_superuser_required
def course_list(request):
    courses = CourseModel.objects.all()
    context = {"courses": courses}
    return render(request, "UI/course/course_dashboard.html", context)


@superuser_required
def assign_teacher(request):
    if request.method == "POST":
        course_id = request.POST.get("course_id")
        teacher_id = request.POST.get("teacher_id")
        try:
            course = CourseModel.objects.get(id=course_id)
            teacher = User.objects.get(id=teacher_id, role="teacher")

            CourseAssignment.objects.get_or_create(course=course, teacher=teacher)
            messages.success(
                request, f"{teacher.username} assigned to {course.name} successfully."
            )
            return redirect("course_dashboard")
        except CourseModel.DoesNotExist:
            messages.error(request, "Course not found.")
        except User.DoesNotExist:
            messages.error(request, "Teacher not found.")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    # Handle GET request: Load the form with courses and teachers
    courses = CourseModel.objects.all()
    teachers = User.objects.filter(role="teacher")
    assignments = CourseAssignment.objects.select_related("course", "teacher").all()
    departments = DepartmentModel.objects.all()
    context = {
        "courses": courses,
        "teachers": teachers,
        "assignments": assignments,
        "departments": departments,
    }
    return render(request, "UI/course/assign_teacher.html", context)


@teacher_or_superuser_required
def course_details(request, pk):
    course = get_object_or_404(CourseModel, id=pk)
    return render(request, "UI/course/course_detail.html", {"course": course})


@superuser_required
def course_delete(request, pk):
    try:
        course = CourseModel.objects.get(id=pk)
        course.delete()
        messages.success(request, "Deleted Successfully")
    except CourseModel.DoesNotExist:
        messages.error(request, "Error Deleting")
        pass
    return redirect("course_dashboard")


@teacher_or_superuser_required
def course_edit(request, pk):
    course = get_object_or_404(CourseModel, id=pk)
    courses = CourseModel.objects.all()
    departments = DepartmentModel.objects.all()
    assignments = CourseAssignment.objects.select_related("course", "teacher").all()

    if request.method == "POST":
        course.name = request.POST.get("course_name")
        course.code = request.POST.get("course_code")
        course.department_id = request.POST.get("course_department")
        course.description = request.POST.get("course_description")
        course.save()
        return redirect("course_dashboard")

    context = {
        "courses": courses,
        "course": course,
        "assignments": assignments,
        "departments": departments,
    }

    return render(request, "UI/course/course_dashboard.html", context)


@teacher_or_superuser_required
def search(request):
    return course_dashboard(request)


@teacher_or_superuser_required
def course_search_ajax(request):
    query = request.GET.get("q", "").strip()

    courses = CourseModel.objects.select_related("department")
    assignments = CourseAssignment.objects.select_related("course", "teacher")

    if query:
        courses = courses.filter(
            Q(name__icontains=query)
            | Q(code__icontains=query)
            | Q(description__icontains=query)
            | Q(department__name__icontains=query)
            | Q(courseassignment__teacher__username__icontains=query)
            | Q(courseassignment__teacher__first_name__icontains=query)
            | Q(courseassignment__teacher__last_name__icontains=query)
        ).distinct()

        assignments = assignments.filter(
            Q(course__name__icontains=query)
            | Q(course__code__icontains=query)
            | Q(course__department__name__icontains=query)
            | Q(teacher__username__icontains=query)
            | Q(teacher__first_name__icontains=query)
            | Q(teacher__last_name__icontains=query)
        ).distinct()

    html = render_to_string(
        "UI/course/course_list_content.html",
        {
            "courses": courses,
            "assignments": assignments,
            "query": query,
        },
    )

    return HttpResponse(html)
