from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Барбершоп "Арбуз"'  # Название приложения в админке

    # метод ready вызывается при запуске приложения и мы можем например импортировать сигналы
    def ready(self):
        # Импортируем сигналы, чтобы они были зарегистрированы при запуске приложения
        import core.signals
