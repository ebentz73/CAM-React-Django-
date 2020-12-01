from django.apps import AppConfig


class MyAppConfig(AppConfig):
    name = 'profile'

    # noinspection PyUnresolvedReferences
    def ready(self):
        import profile.signals
