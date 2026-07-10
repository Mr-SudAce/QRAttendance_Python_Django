from django.urls import path
from QRA_app.Views import course_view

urlpatterns = [
    path("courses/dashboard/", course_view.course_dashboard, name="course_dashboard"),
    path("courses/add/", course_view.add_course, name="add_course"),
    path("courses/assignteacher/", course_view.assign_teacher, name="assign_teacher"),
    path("course/<int:pk>/detail/", course_view.course_details, name="course_detail"),
    path("course/<int:pk>/edit/", course_view.course_edit, name='course_edit'),
    path("course/<int:pk>/delete/", course_view.course_delete, name='course_delete'),
    path("search/", course_view.search, name="search"),
    path("course/search-ajax/", course_view.course_search_ajax, name="course_search_ajax")
]
