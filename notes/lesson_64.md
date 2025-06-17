# Тема Django. User модель. Личный кабинет.  Урок 64

## Стандартная модель пользователя
- Является частью служебного приложения `auth`
- Имеет минмальный набор полей для работы с пользователями:
  - `first_name` - имя (не обязательное)
  - `last_name`
  - `password`
  - `last_login`
  - `is_superuser`
  - `is_staff`
  - `is_active`
  - `email`
  - `username`
  - ... остальные

Требование уникальности только для `username`
Для восстановления пароля, для уведомлений на email это не очень подходит 

Мы можем изменить логику работы формы регистрации так, чтобы проверять уникальность email 
и не позволить пользователю с таким же емейлом зарегистрироваться


## Будем работать с UserRegisterForm в приложении users

- `get_user_model()` - функция, которая возвращает активную модель пользователя




Убрали рендер подсказок из шаблона регистрации

{% if field.help_text %}
    <small class="form-text text-muted">{{ field.help_text }}</small>
{% endif %}

А можно так в инициализаторе класса формы

    # for field_name in ('username', 'password1', 'password2'):
    #     if self.fields.get(field_name): # Проверяем, существует ли поле
    #         self.fields[field_name].help_text = ''


В форму дописали проверку

    # Расширяем логику валидации поля email
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email
    
Теперь пользователь не сможет при регистрации указать email, который уже есть в базе данных


## Собственная модель пользователя

### Спасти базу!

Перед этими действиями желательно сделать бекап важных данных в базе. Например мастеров, услуги, связки... В общем все что есть в приложении `core`
Есть 2 способа. Dump через Django или экспорт через SqliteStudio. На лекции мы сделали второй вариант.

Данные потом залили через редактор.

### Собственная модель пользователя

У нас уже есть приложение для пользователей `users`

В моделях этого приложения мы можем создать свою модель пользователя

Мы должны наследоваться от AbstractUser (Почему? Что это даст?)

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Убираем требование first_name и last_name, если они не обязательны
    first_name = None
    last_name = None

    email = models.EmailField(unique=True) # Делаем email уникальным и обязательным для логина
    
    avatar = models.ImageField(
        upload_to='users/avatars/', 
        null=True, 
        blank=True, 
        verbose_name='Аватар'
    )
    birth_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='Дата рождения'
    )
    telegram_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name='Telegram ID'
    )
    github_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name='GitHub ID'
    )

    # Указываем, что для логина будет использоваться поле email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # username все еще нужен для AbstractUser, но можно сделать его не основным

    def __str__(self):
        return self.email # Или self.username, если предпочитаете

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
```

После этого нам надо указать модель пользователя в settings.py`AUTH_USER_MODEL = 'users.User'`

После чего нам нужно создать миграции
`poetry run python manage.py makemigrations`
`poetry run python manage.py migrate`

