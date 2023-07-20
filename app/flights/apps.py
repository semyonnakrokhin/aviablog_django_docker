from django.apps import AppConfig


class FlightsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'flights'

    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        import flights.signals
