from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Order, Master, Service, Review


class Command(BaseCommand):
    """
    Кастомная команда для создания группы администраторов с определенными правами
    """
    help = 'Создает группу "Администраторы" с правами на просмотр и редактирование заказов, просмотр мастеров, услуг и отзывов'

    def handle(self, *args, **options):
        """Основная логика команды"""
        
        # Создаем или получаем группу администраторов
        admin_group, created = Group.objects.get_or_create(name='Администраторы')
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Группа "Администраторы" успешно создана')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Группа "Администраторы" уже существует')
            )
            # Очищаем существующие права для переназначения
            admin_group.permissions.clear()

        # Получаем типы контента для наших моделей
        order_ct = ContentType.objects.get_for_model(Order)
        master_ct = ContentType.objects.get_for_model(Master)
        service_ct = ContentType.objects.get_for_model(Service)
        review_ct = ContentType.objects.get_for_model(Review)

        # Определяем нужные права
        permissions_to_add = []

        # ЗАКАЗЫ - смотреть и обновлять
        try:
            order_view = Permission.objects.get(
                content_type=order_ct, 
                codename='view_order'
            )
            order_change = Permission.objects.get(
                content_type=order_ct, 
                codename='change_order'
            )
            permissions_to_add.extend([order_view, order_change])
            self.stdout.write('✓ Права на заказы добавлены (просмотр и изменение)')
        except Permission.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Не найдены права для модели Order')
            )

        # МАСТЕРА - только смотреть
        try:
            master_view = Permission.objects.get(
                content_type=master_ct, 
                codename='view_master'
            )
            permissions_to_add.append(master_view)
            self.stdout.write('✓ Права на мастеров добавлены (только просмотр)')
        except Permission.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Не найдены права для модели Master')
            )

        # УСЛУГИ - только смотреть
        try:
            service_view = Permission.objects.get(
                content_type=service_ct, 
                codename='view_service'
            )
            permissions_to_add.append(service_view)
            self.stdout.write('✓ Права на услуги добавлены (только просмотр)')
        except Permission.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Не найдены права для модели Service')
            )

        # ОТЗЫВЫ - только смотреть
        try:
            review_view = Permission.objects.get(
                content_type=review_ct, 
                codename='view_review'
            )
            permissions_to_add.append(review_view)
            self.stdout.write('✓ Права на отзывы добавлены (только просмотр)')
        except Permission.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Не найдены права для модели Review')
            )

        # Назначаем все собранные права группе
        if permissions_to_add:
            admin_group.permissions.set(permissions_to_add)
            self.stdout.write(
                self.style.SUCCESS(f'Назначено {len(permissions_to_add)} прав группе "Администраторы"')
            )
        else:
            self.stdout.write(
                self.style.ERROR('Не удалось назначить права - права не найдены')
            )

        # Выводим сводку по правам
        self.stdout.write('\n--- СВОДКА ПО ПРАВАМ ГРУППЫ "Администраторы" ---')
        for permission in admin_group.permissions.all():
            self.stdout.write(f'• {permission.name}')

        self.stdout.write(
            self.style.SUCCESS('\nГруппа "Администраторы" настроена успешно!')
        )
        self.stdout.write(
            'Теперь вы можете добавить пользователей в эту группу через админку Django'
        )