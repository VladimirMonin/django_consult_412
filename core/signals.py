# Опишем сигнал, который будет слушать создание записи в модель Review и проверять есть ли в поле text слова "плохо" или "ужасно". - Если нет, то меняем is_published на True

from .models import Order, Review
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .mistral import moderate_review
# Импорт всего что нужно для работы бота
from .telegram_bot import send_telegram_message
from asyncio import run
# Из настроек импортируем токен и id чата
from django.conf import settings

TELEGRAM_BOT_API_KEY = settings.TELEGRAM_BOT_API_KEY
TELEGRAM_USER_ID = settings.TELEGRAM_USER_ID

@receiver(post_save, sender=Review)
def check_review_text(sender, instance, created, **kwargs):
    """
    Проверяет текст отзыва на наличие слов "плохо" или "ужасно".
    Если таких слов нет, то устанавливает is_published в True.
    """
    if created:
        if not moderate_review(instance.text):
            instance.is_published = True
            instance.save()
            # Вывод в терминал 
            print(f"Отзыв '{instance.client_name}' опубликован автоматически.")
        else:
            instance.is_published = False
            instance.save()
            # Вывод в терминал 
            print(f"Отзыв '{instance.client_name}' не опубликован из-за негативных слов.")


# А теперь так же но с ожиданем m2m_changed
# Order.services.through - это промежуточная таблица между Order и Service (Многие ко многим)
# Мы ожидаем событие m2m_changed, когда туда запишутся новые связи
@receiver(m2m_changed, sender=Order.services.through)
def send_telegram_notification(sender, instance, action, **kwargs):
    """
    Обработчик сигнала m2m_changed для модели Order.
    Он обрабатывает добавление КАЖДОЙ услуги в запись на консультацию.
    
    """
    # action == 'post_add' - это значит что в промежуточную таблицу добавили новую связь. НО нам надо убедится что это именно добавление новой связи, а не удаление или изменение
    # pk_set - это список id услуг которые были добавлены в запись (формируется только при создании Order или удалении)
    # Комбинация позволяет ТОЧНО понять что это именно создание НОВОЙ услуги и что все M2M связи уже созданы
    if action == 'post_add' and kwargs.get('pk_set'):
        # Получаем список услуг
        services = [service.name for service in instance.services.all()]

        # Форматирование даты и времени для желаемой даты записи, и даты создания услуги
        if instance.appointment_date:
            appointment_date = instance.appointment_date.strftime("%d.%m.%Y %H:%M")
        else:
            appointment_date = 'не указана'

        # Форматируем дату создания
        date_created = instance.date_created.strftime("%d.%m.%Y %H:%M")

        # Формируем сообщение
        message = f"""
*Новая запись на консультацию* 

*Имя:* {instance.client_name} 
*Телефон:* {instance.phone or 'не указан'} 
*Комментарий:* {instance.comment or 'не указан'}
*Услуги:* {', '.join(services) or 'не указаны'}
*Дата создания:* {date_created}
*Мастер:* {instance.master.first_name} {instance.master.last_name}
*Желаемая дата записи:* {appointment_date}
*Ссылка на админ-панель:* http://127.0.0.1:8000/admin/core/order/{instance.id}/change/

#запись #{instance.master.last_name.lower()}
-------------------------------------------------------------
"""
        run(send_telegram_message(TELEGRAM_BOT_API_KEY, TELEGRAM_USER_ID, message))
