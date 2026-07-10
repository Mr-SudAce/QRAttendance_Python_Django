from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from QRA_main import settings

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("", include("QRA_app.routes.main_urls")),
        path("", include("QRA_app.auth.auth_urls")),
        path("", include("QRA_app.routes.teacher_urls")),
        path("", include("QRA_app.routes.student_urls")),
        path("", include("QRA_app.routes.course_urls")),
        path("", include("QRA_app.routes.department_urls")),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
