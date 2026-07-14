import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth import views as django_auth_views
from django.http import HttpResponseRedirect
from django.urls import reverse
from QRA_app.auth.handler.auth_handler import register_view
from QRA_app.auth.handler.helper_func import *
from QRA_app.models import User
from QRA_app.permission import *
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator


class CustomPasswordResetView(django_auth_views.PasswordResetView):
    def form_valid(self, form):
        email = form.cleaned_data.get("email", "")
        users = form.get_users(email)
        user = next(iter(users), None)
        extra_email_context = None

        if user is not None:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            extra_email_context = {
                "reset_link": self.request.build_absolute_uri(
                    reverse(
                        "password_reset_confirm",
                        kwargs={"uidb64": uid, "token": token},
                    )
                )
            }

        form.save(
            request=self.request,
            use_https=self.request.is_secure(),
            email_template_name=self.email_template_name,
            subject_template_name=self.subject_template_name,
            html_email_template_name=self.html_email_template_name,
            extra_email_context=extra_email_context,
        )
        return HttpResponseRedirect(self.get_success_url())


# =========================
# LOGIN VIEWS
# =========================
def superuser_login_view(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("superuser_dashboard")

    if is_login_locked(request):
        return render(
            request,
            "counterpage.html",
            {
                "remaining_seconds": get_remaining_seconds(request),
                "redirect_url_name": "superuser_login",
                "max_attempts": MAX_LOGIN_ATTEMPTS,
                "lock_minutes": LOCKOUT_MINUTES,
            },
        )

    if request.method == "POST":
        identifier = request.POST.get("identifier")
        password = request.POST.get("password")

        user_obj = get_user_by_identifier(identifier)

        if user_obj is None:
            register_failed_attempt(request)
            messages.error(request, "Invalid login credentials")
            return redirect("superuser_login")

        user = authenticate(
            request,
            username=user_obj.username,
            password=password,
        )

        if user is not None and user.is_superuser:
            clear_login_attempts(request)
            login(request, user)
            request.session.set_expiry(SESSION_TIMEOUT)
            return redirect("superuser_dashboard")

        register_failed_attempt(request)
        messages.error(
            request,
            "Invalid credentials or not a superuser account.",
        )
        return redirect("superuser_login")
    return render(request, "auth/superuser_login.html")


def student_login_view(request):
    if (
        request.user.is_authenticated
        and hasattr(request.user, "role")
        and request.user.role == "student"
    ):
        return redirect("student_dashboard")

    # BLOCK LOGIN IF LOCKED
    if is_login_locked(request):
        return render(
            request,
            "counterpage.html",
            {
                "remaining_seconds": get_remaining_seconds(request),
                "redirect_url_name": "student_login",
                "max_attempts": MAX_LOGIN_ATTEMPTS,
                "lock_minutes": LOCKOUT_MINUTES,
            },
        )

    if request.method == "POST":
        identifier = request.POST.get("identifier")
        password = request.POST.get("password")

        user_obj = get_user_by_identifier(identifier)

        # USER NOT FOUND → COUNT AS FAILED ATTEMPT
        if user_obj is None:
            register_failed_attempt(request)
            messages.error(request, "Invalid login credentials")
            return redirect("student_login")

        # AUTHENTICATE
        user = authenticate(
            request,
            username=user_obj.username,
            password=password,
        )

        # SUCCESS LOGIN
        if user is not None and user.role == "student":
            clear_login_attempts(request)
            login(request, user)
            request.session.set_expiry(SESSION_TIMEOUT)
            return redirect("student_dashboard")

        # FAILED LOGIN → COUNT ATTEMPT
        register_failed_attempt(request)
        messages.error(
            request,
            "Invalid credentials or not a student account.",
        )
        return redirect("student_login")
    return render(request, "auth/student_login.html")


def teacher_login_view(request):
    if (
        request.user.is_authenticated
        and hasattr(request.user, "role")
        and request.user.role == "teacher"
    ):
        return redirect("teacher_dashboard")

    if is_login_locked(request):
        return render(
            request,
            "counterpage.html",
            {
                "remaining_seconds": get_remaining_seconds(request),
                "redirect_url_name": "teacher_login",
                "max_attempts": MAX_LOGIN_ATTEMPTS,
                "lock_minutes": LOCKOUT_MINUTES,
            },
        )

    if request.method == "POST":
        identifier = request.POST.get("identifier")
        password = request.POST.get("password")

        user_obj = get_user_by_identifier(identifier)

        if user_obj is None:
            register_failed_attempt(request)
            messages.error(request, "Invalid login credentials")
            return redirect("teacher_login")

        user = authenticate(
            request,
            username=user_obj.username,
            password=password,
        )

        if user is not None and user.role == "teacher":
            clear_login_attempts(request)
            login(request, user)
            request.session.set_expiry(SESSION_TIMEOUT)
            return redirect("teacher_dashboard")

        register_failed_attempt(request)
        messages.error(
            request,
            "Invalid credentials or not a teacher account.",
        )
        return redirect("teacher_login")
    return render(request, "auth/teacher_login.html")


# =========================
# REGISTER VIEWS
# =========================


def student_register_view(request):
    return register_view(
        request,
        role="student",
        redirect_url="student_login",
        render_template="auth/student_register.html",
    )


def teacher_register_view(request):
    return register_view(
        request,
        role="teacher",
        redirect_url="teacher_login",
        render_template="auth/teacher_register.html",
    )


# =========================
# LOGOUT VIEWS
# =========================
def teacher_logout_view(request):
    logout(request)
    return redirect("teacher_login")


def student_logout_view(request):
    logout(request)
    return redirect("student_login")


def superuser_logout_view(request):
    logout(request)
    return redirect("superuser_login")


# =========================
# CHANGE PASSWORD VIEWS
# =========================
@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            if request.user.role == "teacher":
                return redirect("teacher_dashboard")
            elif request.user.role == "student":
                return redirect("student_dashboard")
            else:
                return redirect("superuser_dashboard")

    else:
        form = PasswordChangeForm(request.user)

    return render(request, "auth/change_pw.html", {"form": form})


# =========================
# RESET PASSWORD VIEWS
# =========================
def password_reset_confirm(request, uidb64=None, token=None):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(
                    request, "Your password has been set. You may go ahead and log in now."
                )
                return redirect("password_reset_complete")
        else:
            form = SetPasswordForm(user)
        return render(
            request, "auth/resetpw/password_reset_confirm.html", {"form": form}
        )
    else:
        return render(request, "auth/resetpw/password_reset_invalid.html")
    
    
def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get('email')
        CustomUser = get_user_model()
        associated_users = CustomUser.objects.filter(email=email)

        if associated_users.exists():
            for single_user in associated_users:
                uid = urlsafe_base64_encode(force_bytes(single_user.pk))
                token = default_token_generator.make_token(single_user)

                reset_link = f"{os.getenv('BASE_URL')}/reset/{uid}/{token}/" 
                context = {
                    'username': single_user.username,
                    'reset_link': reset_link,
                    'user_email': single_user.email,
                    'trigger_email': True
                }
                return render(request, "auth/resetpw/password_reset_done.html", context)
        
        return render(request, "auth/resetpw/password_reset_done.html", {'trigger_email': False})
        
    return render(request, "auth/resetpw/password_reset_form.html")
