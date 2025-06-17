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