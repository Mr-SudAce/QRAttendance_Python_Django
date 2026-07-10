from django.contrib import admin

from QRA_app.models import (
    User,
    DepartmentModel,
    CourseModel,
    EnrollmentModel,
    AttendanceSessionModel,
    AttendanceRecordModel,
    DeviceLogModel,
    AttendanceSummaryModel,
)

# Register your models here.

admin.site.register(User)
admin.site.register(DepartmentModel)
admin.site.register(CourseModel)
admin.site.register(EnrollmentModel)
admin.site.register(AttendanceSessionModel)
admin.site.register(AttendanceRecordModel)
admin.site.register(DeviceLogModel)
admin.site.register(AttendanceSummaryModel)