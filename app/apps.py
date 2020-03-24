from django.apps import AppConfig


class MyAppConfig(AppConfig):
    name = 'app'

    # noinspection PyUnresolvedReferences
    def ready(self):
        import app.signals
