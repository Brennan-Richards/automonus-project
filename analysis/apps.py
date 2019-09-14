from django.apps import AppConfig
from django.conf import settings


class AnalysisConfig(AppConfig):
    name = 'analysis'

    def ready(self):
        from . import scheduler
        if settings.SCHEDULER_AUTOSTART:
            scheduler.start()