from django.apps import AppConfig



class QRAAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'QRA_app'

    def ready(self):
        import QRA_app.signals
