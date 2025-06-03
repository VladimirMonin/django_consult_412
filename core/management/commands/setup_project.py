from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import transaction


class Command(BaseCommand):
    """
    Команда для быстрого развертывания проекта
    Выполняет миграции и создает суперпользователя
    """
    help = 'Запускает миграции и создает суперпользователя admin с паролем admin'

    def handle(self, *args, **options):
        """Основная логика команды развертывания"""
        
        self.stdout.write(
            self.style.SUCCESS('=== НАЧИНАЕМ РАЗВЕРТЫВАНИЕ ПРОЕКТА ===\n')
        )

        # Шаг 1: Запускаем миграции
        try:
            self.stdout.write('1. Запускаем миграции...')
            call_command('migrate', verbosity=1, interactive=False)
            self.stdout.write(
                self.style.SUCCESS('✓ Миграции выполнены успешно\n')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Ошибка при выполнении миграций: {e}\n')
            )
            return

        # Шаг 2: Создаем суперпользователя
        try:
            self.stdout.write('2. Создаем суперпользователя...')
            
            User = get_user_model()
            
            # Проверяем, существует ли уже пользователь admin
            if User.objects.filter(username='admin').exists():
                self.stdout.write(
                    self.style.WARNING('! Пользователь admin уже существует, пропускаем создание')
                )
            else:
                # Создаем суперпользователя в транзакции для безопасности
                with transaction.atomic():
                    admin_user = User.objects.create_superuser(
                        username='admin',
                        email='ad@ad.ru',
                        password='admin'
                    )
                    self.stdout.write(
                        self.style.SUCCESS('✓ Суперпользователь admin создан успешно')
                    )
                    self.stdout.write(f'  Логин: admin')
                    self.stdout.write(f'  Пароль: admin')
                    self.stdout.write(f'  Email: ad@ad.ru\n')
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Ошибка при создании суперпользователя: {e}\n')
            )
            return

        # Финальное сообщение
        self.stdout.write(
            self.style.SUCCESS('=== ЗАВЕРШЕНО ===')
        )
