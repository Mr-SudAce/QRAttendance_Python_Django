from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver

User = get_user_model()


@receiver(post_migrate)
def create_default_superuser(sender, **kwargs):
    if not User.objects.filter(username="superadmin").exists():
        User.objects.create_superuser(
            first_name="Super",
            last_name="Admin",
            role="superuser",
            is_staff=True,
            is_superuser=True,
            username="superadmin",
            email="superadmin@gmail.com",
            password="superadmin123"
        )
        print("🔥 Default superuser created: superadmin/superadmin123")