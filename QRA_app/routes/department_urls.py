from django.urls import path
from QRA_app.Views import department_views


urlpatterns = [
    path("departments/dashboard/", department_views.department_dashboard, name="department_dashboard"),
    path("departments/add/", department_views.add_department, name="add_department"),
    path("departments/", department_views.department_list, name="department_list"),
    path("departments/<int:department_id>/", department_views.department_detail, name="department_detail"),
    path('departments/<int:pk>/delete', department_views.department_delete, name='department_delete'),
    path('departments/edit/<int:pk>/', department_views.department_edit, name='department_edit'),
    path("department/search-ajax/", department_views.dept_search_ajax, name="dept_search_ajax"),
    path("search/", department_views.search, name="dept_search"),
]
