from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import redirect, render
from QRA_app.models import User

MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_MINUTES = 1
SESSION_TIMEOUT = 1800 # 30 minutes in seconds


def get_remaining_seconds(request):
    lock_started = request.session.get("lock_started")
    if not lock_started:
        return 0
    lock_started = datetime.fromisoformat(lock_started)
    lock_until = lock_started + timedelta(minutes=LOCKOUT_MINUTES)
    remaining = (lock_until - timezone.now()).total_seconds()
    if remaining <= 0:
        clear_login_attempts(request)
        return 0
    return int(remaining)


def is_login_locked(request):
    return get_remaining_seconds(request) > 0


def register_failed_attempt(request):
    attempts = request.session.get("login_attempts", 0) + 1
    request.session["login_attempts"] = attempts

    if attempts >= MAX_LOGIN_ATTEMPTS:
        request.session["lock_started"] = timezone.now().isoformat()


def clear_login_attempts(request):
    request.session.pop("login_attempts", None)
    request.session.pop("lock_started", None)


def get_user_by_identifier(identifier):
    if not identifier:
        messages.error("No credentials provided.")
        return None
    try:
        return User.objects.get(username=identifier)
    except User.DoesNotExist:
        message = f"User with username '{identifier}' does not exist."
        messages.error(message)

    try:
        return User.objects.get(email=identifier)
    except User.DoesNotExist:
        message = f"User with email '{identifier}' does not exist."
        messages.error(message)

    try:
        return User.objects.get(phone_number=identifier)
    except User.DoesNotExist:
        message = f"User with phone number '{identifier}' does not exist."
        messages.error(message)
    return
