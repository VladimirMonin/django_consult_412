# Lesson 65. Восстановление пароля через email

## Маршруты для сброса пароля

### Маршрут авторизации `users/login/`

Форма для входа на сайт. Если забыли пароль, то можно восстановить его через email - надо нажать кнопку "забыли пароль?"

`users/login/` - страница входа
`LoginView` - класс, который обрабатывает запросы на вход (служебный)
`AuthenticationForm` - форма для входа
`login.html` - шаблон для страницы входа
`UserLoginView` - класс, который обрабатывает запросы на вход наследуется от `LoginView`

Добавили ссылку на восстановление пароля в шаблоне `login.html`

```html
<p class="text-center">
            Забыли пароль? <a href="{% url 'users:password_reset' %}">Восстановить</a>
        </p>
```

### Маршрут для сброса пароля `users/password-reset/`

Форма для сброса пароля. Надо ввести email, на который будет отправлена ссылка для сброса пароля.

`users/password-reset/` - страница сброса пароля
`PasswordResetView` - класс, который обрабатывает запросы на сброс пароля (сллужебный)
`PasswordResetForm` - форма для сброса пароля (сллужебный)
`password_reset_form.html` - шаблон для страницы сброса пароля
`name='password_reset'` - имя маршрута для сброса пароля
`CustomPasswordResetView` - класс, который обрабатывает запросы на сброс пароля наследуется от `PasswordResetView`
`CustomPasswordResetForm` - форма для сброса пароля наследуется от `PasswordResetForm`

```python
class CustomPasswordResetForm(PasswordResetForm):
    """Кастомная форма для сброса пароля."""
    def __init__(self, *args, **kwargs):
        """Инициализация формы сброса пароля: настройка полей."""
        super().__init__(*args, **kwargs)
        # Кастомизация поля email
        self.fields['email'].widget.attrs.update({
            'class': 'form-control mb-2',
            'placeholder': 'Email'
        })
```




### Маршрут для сброса пароля по ссылке `users/reset/<uidb64>/<token>/`
Форма для сброса пароля. Надо ввести новый пароль.