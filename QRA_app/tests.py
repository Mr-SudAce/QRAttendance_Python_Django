import importlib
import os
from unittest.mock import patch

from django.core import mail
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.contrib.auth.forms import PasswordResetForm

from QRA_app.auth.auth_views import CustomPasswordResetView
from QRA_app.models import User


class PasswordResetSettingsTests(SimpleTestCase):
    def test_defaults_to_console_backend_without_smtp_credentials(self):
        import QRA_main.settings as settings_module

        with patch.dict(os.environ, {"EMAIL_HOST_USER": "", "EMAIL_HOST_PASSWORD": ""}, clear=False):
            reloaded = importlib.reload(settings_module)
            self.assertEqual(
                reloaded.EMAIL_BACKEND,
                "django.core.mail.backends.console.EmailBackend",
            )

        importlib.reload(settings_module)


class PasswordResetViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_custom_password_reset_view_sends_reset_email(self):
        user = User.objects.create_user(
            username="resetuser",
            email="resetuser@example.com",
            password="StrongPassword123!",
        )

        request = self.factory.post(
            "/password_reset/",
            {"email": user.email},
        )
        request.user = None
        request.session = {}

        view = CustomPasswordResetView()
        view.request = request
        view.args = ()
        view.kwargs = {}

        form = PasswordResetForm(data={"email": user.email})
        self.assertTrue(form.is_valid())

        response = view.form_valid(form)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("resetuser@example.com", mail.outbox[0].to)
        self.assertIn("/reset/", mail.outbox[0].body)
