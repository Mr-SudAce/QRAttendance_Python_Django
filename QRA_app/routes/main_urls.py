from django.urls import path
from ..Views import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.superuser_dashboard, name="superuser_dashboard"),
    
]
