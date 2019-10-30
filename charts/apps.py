from django.apps import AppConfig
from django.conf import settings


class ChartsConfig(AppConfig):
    name = 'charts'

    def ready(self):
        from . import scheduler
        if settings.SCHEDULER_AUTOSTART:
            scheduler.start()
