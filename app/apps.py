from django.apps import AppConfig
from material.frontend.apps import ModuleMixin


class MyAppConfig(ModuleMixin, AppConfig):
    name = 'app'
    verbose_name = 'Cloud Analysis Manager'
    icon = '<i class="material-icons">settings_applications</i>'

    # noinspection PyUnresolvedReferences
    def ready(self):
        import app.money_patch
        import app.signals
