from django.shortcuts import render, redirect
from django.http import *
from QRA_app.permission import *
from django.template.loader import render_to_string
from QRA_app.models import *
from django.contrib import messages
from django.db.models import Q


@superuser_required
def department_dashboard(request):
    departments = DepartmentModel.objects.all()
    headers = ["Department Name, Action"]
    context = {"headers": headers, "departments": departments}
    return render(request, "UI/department/department_dashboard.html", context)


@superuser_required
def add_department(request):
    if request.method == "POST":
        try:
            name = request.POST.get("department_name")
            description = request.POST.get("department_description")

            if not name:
                messages.error(request, "Department name is required.")
                return render(request, "UI/department/add_department.html")

            if DepartmentModel.objects.filter(name=name).exists():
                messages.warning(request, "Department already exists.")
                return render(request, "UI/department/add_department.html")

            DepartmentModel.objects.create(name=name, description=description)
            messages.success(request, "Department added successfully")
            return redirect("department_dashboard")
        except Exception as e:
            messages.error(request, f"Error adding department: {str(e)}")
            return render(request, "UI/department/add_department.html")

    return render(request, "UI/department/department_dashboard.html")


@superuser_required
def department_list(request):
    departments = DepartmentModel.objects.all()
    return render(
        request, "UI/department/department_dashboard.html", {"departments": departments}
    )


@superuser_required
def department_delete(request, pk):
    try:
        dept = DepartmentModel.objects.get(id=pk)
        dept.delete()
        messages.success(request, 'Deleted Successfully')
    except DepartmentModel.DoesNotExist:
        messages.error(request, 'Error Deleting')
        pass
    return redirect("department_dashboard")


@superuser_required
def department_edit(request, pk):
    departments = DepartmentModel.objects.all()
    try:
        dept = DepartmentModel.objects.get(id=pk)
    except DepartmentModel.DoesNotExist:
        return redirect("department_dashboard")

    if request.method == "POST":
        dept.name = request.POST.get("department_name")
        dept.description = request.POST.get("department_description")
        dept.save()
        return redirect("department_dashboard")

    return render(
        request,
        "UI/department/department_dashboard.html",
        {"dept": dept, "departments": departments},
    )


@superuser_required
def department_detail(request, department_id):
    department = DepartmentModel.objects.get(id=department_id)
    return render(
        request, "UI/department/department_detail.html", {"department": department}
    )

@superuser_required
def search(request):
    return department_dashboard(request)

@superuser_required
def dept_search_ajax(request):
    query = request.GET.get("q", "").strip()

    departments = DepartmentModel.objects.all()
    
    if query:
        departments = departments.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        ).distinct()

    html = render_to_string(
        "UI/department/department_list_content.html",
        {
            "departments": departments,
            "query": query,
        },
    )

    return HttpResponse(html)


