from django.utils import timezone
import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser


##########################
# UserModel
##########################
class User(AbstractUser):
    USER_ROLE = (
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("superuser", "Superuser"),
    )
    role = models.CharField(max_length=10, choices=USER_ROLE, default="student")
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = "superuser"
        elif self.is_staff:
            self.role = "teacher"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


##########################
# Department Model
##########################
class DepartmentModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

##########################
# Course/Class Model
##########################
class CourseModel(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    department = models.ForeignKey(
        DepartmentModel,
        on_delete=models.CASCADE,
        related_name="courses"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

##########################
# Course Assignment Model
##########################
class CourseAssignment(models.Model):
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="course_assignments")
    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ("course", "teacher")

    def __str__(self):
        return f"{self.teacher.username} assigned to {self.course.name}"
    
##########################
# Enrollment Model
##########################
class EnrollmentModel(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(
        CourseModel, on_delete=models.CASCADE, related_name="enrollments"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "course")
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["course"]),
        ]

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.name}"


##########################
# Attendance Session Model
##########################
class AttendanceSessionModel(models.Model):
    course = models.ForeignKey(
        CourseModel, on_delete=models.CASCADE, related_name="attendance_sessions"
    )
    session_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    session_name = models.CharField(max_length=100)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def qr_url(self):
        return f"/student/scan/{self.session_token}"

    def __str__(self):
        return f"{self.session_name} for {self.course.name} on {self.expires_at.strftime('%Y-%m-%d %H:%M')}"


##########################
# Attendance Record Model
##########################
class AttendanceRecordModel(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="attendance_records"
    )
    attendance_session = models.ForeignKey(
        AttendanceSessionModel,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    status = models.CharField(
        max_length=20,
        choices=[("present", "Present"), ("absent", "Absent")],
        default="absent",
    )
    device_info = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "attendance_session")

    def __str__(self):
        return f"{self.student.username} - {self.attendance_session.course.name} - {self.status} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"


##########################
# Log Model
##########################
class DeviceLogModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="device_logs")
    device_hash = models.CharField(max_length=64, db_index=True)
    last_used = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Device {self.device_hash} used by {self.user.username} on {self.last_used.strftime('%Y-%m-%d %H:%M')}"


##########################
# Attendance Summary
##########################


class AttendanceSummaryModel(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE)
    attendance_percentage = models.FloatField(default=0)
    total_present = models.IntegerField(default=0)
    total_sessions = models.IntegerField(default=0)

    def calculate_percentage(self):

        if self.total_sessions > 0:

            self.attendance_percentage = (
                self.total_present / self.total_sessions
            ) * 100

        return self.attendance_percentage
