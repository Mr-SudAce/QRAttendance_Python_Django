from django.contrib.auth.decorators import user_passes_test


# =========================
# ROLE CHECKS
# =========================
def is_teacher(user):
    return user.is_authenticated and user.role == "teacher"


def is_student(user):
    return user.is_authenticated and user.role == "student"


def is_superuser(user):
    return user.is_authenticated and user.is_superuser


def is_teacher_or_superuser(user):
    return user.is_authenticated and (
        user.role == "teacher" or user.is_superuser
    )


def is_student_or_teacher(user):
    return user.is_authenticated and user.role in ["student", "teacher"]


# =========================
# DECORATORS
# =========================
teacher_required = user_passes_test(
    is_teacher,
    login_url="teacher_login",
)

student_required = user_passes_test(
    is_student,
    login_url="student_login",
)

superuser_required = user_passes_test(
    is_superuser,
    login_url="superuser_login",
)

teacher_or_superuser_required = user_passes_test(
    is_teacher_or_superuser,
    login_url="teacher_login",
)