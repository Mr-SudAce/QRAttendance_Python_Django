from django.urls import path
from QRA_app.auth import auth_views
from django.contrib.auth import views as django_auth_views

urlpatterns = [
    # Login URLs - Modern structure
    path("login/admin/", auth_views.superuser_login_view, name="superuser_login"),
    path("login/", auth_views.student_login_view, name="student_login"),
    path("login/teacher/", auth_views.teacher_login_view, name="teacher_login"),
    
    # Register URLs
    path("register/", auth_views.student_register_view, name="student_register"),
    path("register/teacher/", auth_views.teacher_register_view, name="teacher_register"),
    
    # Logout URLs
    path("logout/admin/", auth_views.superuser_logout_view, name="superuser_logout"),
    path("logout/", auth_views.student_logout_view, name="student_logout"),
    path("logout/teacher/", auth_views.teacher_logout_view, name="teacher_logout"),
    
    # Change pw
    path('change/pw/', auth_views.change_password, name='change_password'),
    
    path('password_reset/', auth_views.CustomPasswordResetView.as_view(template_name='auth/registration/password_reset_form.html', email_template_name='auth/registration/password_reset_email.html', subject_template_name='auth/registration/password_reset_subject.txt'), name='password_reset'),
    
    path('password_reset/done/', django_auth_views.PasswordResetDoneView.as_view(template_name='auth/registration/password_reset_done.html'), name='password_reset_done'),
    
    path('reset/<str:uidb64>/<str:token>/', auth_views.password_reset_confirm, name='password_reset_confirm'),
    
    path('reset/done/', django_auth_views.PasswordResetCompleteView.as_view(template_name='auth/registration/password_reset_complete.html'), name='password_reset_complete'),
    
]
