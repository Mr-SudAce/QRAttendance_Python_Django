from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from QRA_app.models import *
from ...generate_username import *
from django.contrib.auth import authenticate, login


# def login_view(request, role, redirect_login, redirect_dashboard, render_template):
#     if request.method == "POST":
#         identifier = request.POST.get("identifier")
#         password = request.POST.get("password")
#         try:
#             user_obj = User.objects.get(username=identifier)
#         except User.DoesNotExist:
#             user_obj = None

#         if user_obj is None:
#             try:
#                 user_obj = User.objects.get(email=identifier)
#             except User.DoesNotExist:
#                 user_obj = None

#         if user_obj is None:
#             try:
#                 user_obj = User.objects.get(phone_number=identifier)
#             except User.DoesNotExist:
#                 user_obj = None

#         if user_obj is None:
#             messages.error(request, "Invalid login credentials")
#             return redirect(redirect_login)
#         user = authenticate(request, username=user_obj.username, password=password)

#         if user is not None and user.role == role:
#             login(request, user)
#             return redirect(redirect_dashboard)
#         messages.error(
#             request, f"Invalid credentials or not a {role} account.".format(role=role)
#         )
#         return redirect(redirect_login)
#     return render(request, render_template)


def register_view(request, role, redirect_url, render_template):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        profile_picture = request.FILES.get("profile_picture")
        address = request.POST.get("address")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")

        if not first_name or not last_name or not password:
            return HttpResponse("Missing required fields")

        if User.objects.filter(email=email).exists():
            return HttpResponse("Email already exists")

        try:
            User.objects.create_user(
                username=generate_username(first_name=first_name, last_name=last_name),
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                profile_picture=profile_picture,
                address=address,
                phone_number=phone_number,
                email=email,
                is_staff=False,
            )
            return redirect(redirect_url)
        except Exception as e:
            return HttpResponse(f"Registration failed: {e}")

    return render(request, f"{render_template}")
