# Django Forms: Поля, Валидаторы, Атрибуты и Виджеты

## Общий механизм валидации форм в Django

Django предоставляет мощную систему валидации данных форм. Когда форма обрабатывает данные, происходит несколько этапов валидации:

1. **Валидация отдельных полей** - проверки на уровне каждого поля (тип, обязательность, длина и т.д.)
2. **Специфическая валидация полей** через методы `clean_<имя_поля>()` 
3. **Общая валидация формы** через метод `clean()`

### Метод clean() и порядок валидации

Метод `clean()` является самым важным в системе валидации Django-форм. Он запускается после всех валидаторов отдельных полей и методов `clean_<имя_поля>()`. Особенности метода `clean()`:

- Используется для валидации, зависящей от нескольких полей (например, сравнение пароля и подтверждения)
- При переопределении **обязательно** вызывайте родительский метод через `super().clean()`  
- Возвращает полный словарь очищенных данных `cleaned_data`
- Для добавления ошибок используйте `self.add_error('поле', 'сообщение')` или `raise ValidationError('сообщение')` 

```python
def clean(self):
    # Вызываем родительский метод - это критически важно!
    cleaned_data = super().clean()
    
    password = cleaned_data.get('password')
    password_confirm = cleaned_data.get('password_confirm')
    
    # Валидация на основе нескольких полей
    if password and password_confirm and password != password_confirm:
        # Добавляем ошибку к конкретному полю
        self.add_error('password_confirm', 'Пароли не совпадают')
        
    return cleaned_data  # Важно возвращать cleaned_data
```

### Методы clean_<имя_поля>() для специфической валидации

Django автоматически вызывает методы вида `clean_<имя_поля>()` для каждого поля формы. Эти методы позволяют добавить специфическую логику валидации для конкретного поля:

```python
def clean_email(self):
    email = self.cleaned_data.get('email')
    
    # Проверяем, что email не используется другим пользователем
    if User.objects.filter(email=email).exists():
        raise ValidationError('Этот email уже зарегистрирован в системе')
    
    # Проверяем корпоративный домен
    if not email.endswith('@company.com'):
        raise ValidationError('Разрешены только корпоративные адреса')
        
    # Обязательно возвращаем очищенное значение поля!
    return email
```

Важные правила при работе с методами `clean_<имя_поля>()`:
- Метод должен начинаться с префикса `clean_`, за которым следует точное имя поля
- Метод должен извлекать значение из `self.cleaned_data.get('имя_поля')`
- Для обозначения ошибки используйте `raise ValidationError('сообщение')`
- Метод **обязательно** должен возвращать очищенное значение поля

## Работа с ошибками формы

Django предоставляет два типа ошибок при валидации формы:

### 1. Ошибки, связанные с конкретными полями

Это ошибки, которые связаны с определенным полем формы. Они доступны через атрибут `errors` формы и через атрибут `errors` каждого поля:

```python
# В представлении
if form.is_valid():
    # обработка данных
else:
    print(form.errors)  # {'name': ['Обязательное поле.'], 'email': ['Введите корректный email.']}
```

```django
{# В шаблоне #}
{% for field in form %}
    {% for error in field.errors %}
        <div class="alert alert-danger">{{ error }}</div>
    {% endfor %}
{% endfor %}
```

Эти ошибки возникают при:
- Встроенной валидации полей (required=True, max_length и т.д.)
- При вызове `raise ValidationError()` в методах `clean_<имя_поля>()`
- При вызове `self.add_error('имя_поля', 'сообщение')` в методе `clean()`

### 2. Ошибки, не связанные с полями (non-field errors)

Эти ошибки связаны с формой в целом, а не с конкретным полем. Они возникают:
- При вызове `raise ValidationError()` в методе `clean()` (без указания поля)
- При вызове `self.add_error(None, 'сообщение')` 

```python
def clean(self):
    cleaned_data = super().clean()
    start_date = cleaned_data.get('start_date')
    end_date = cleaned_data.get('end_date')
    
    if start_date and end_date and start_date > end_date:
        # Ошибка, не связанная с конкретным полем
        raise ValidationError('Дата начала не может быть позже даты окончания')
    
    return cleaned_data
```

```django
{# Вывод ошибок, не связанных с полями #}
{% for error in form.non_field_errors %}
    <div class="alert alert-danger">{{ error }}</div>
{% endfor %}
```

### Настройка сообщений об ошибках

Django позволяет настраивать сообщения об ошибках через атрибут `error_messages` для каждого поля:

```python
name = forms.CharField(
    max_length=100,
    error_messages={
        'required': 'Пожалуйста, введите ваше имя',
        'max_length': 'Имя не должно превышать 100 символов',
    }
)
```

Стандартные ключи для `error_messages` включают:
- `required` - поле обязательно для заполнения
- `invalid` - формат данных неверен
- `max_length` - превышена максимальная длина
- `min_length` - не достигнута минимальная длина
- `max_value` - превышено максимальное значение
- `min_value` - не достигнуто минимальное значение
- `invalid_choice` - неверный выбор в ChoiceField

## Обработка данных формы и метод is_valid()

Когда мы обрабатываем данные формы в представлении Django, типичный паттерн выглядит так:

```python
def my_view(request):
    if request.method == 'POST':
        # Создаем экземпляр формы с данными из запроса
        form = MyForm(request.POST, request.FILES)
        
        # Проверяем валидность формы
        if form.is_valid():
            # Получаем очищенные данные
            cleaned_data = form.cleaned_data
            # Обрабатываем данные (например, сохраняем в БД)
            # ...
            return redirect('success-url')
    else:
        # Создаем пустую форму для GET-запроса
        form = MyForm()
    
    # Если форма не валидна или это GET-запрос, рендерим шаблон с формой
    return render(request, 'template.html', {'form': form})
```

### Как работает метод is_valid()

Метод `is_valid()` является ключевым для обработки форм. При его вызове происходит следующее:

1. **Обработка данных**: Все данные из `request.POST` (и `request.FILES`, если указано) преобразуются в Python-объекты
2. **Запуск валидаторов полей**: Проверяются все встроенные валидаторы для каждого поля (required, max_length и т.д.)
3. **Вызов clean_<имя_поля>()**: Для каждого поля вызывается соответствующий метод, если он определен
4. **Вызов clean()**: Выполняется общая валидация формы через метод `clean()`
5. **Результат**: Если все проверки пройдены успешно, `is_valid()` возвращает `True`, иначе - `False`
6. **Создание cleaned_data**: При успешной валидации создается словарь `cleaned_data` с очищенными данными

Важно помнить, что `cleaned_data` содержит только валидные поля. Если какое-то поле не прошло валидацию, его не будет в `cleaned_data`.

### Доступ к очищенным данным

После успешной валидации мы можем получить очищенные данные через атрибут `cleaned_data`:

```python
if form.is_valid():
    name = form.cleaned_data.get('name')
    email = form.cleaned_data.get('email')
    message = form.cleaned_data.get('message')
    # Используем очищенные данные
```

Всегда используйте метод `.get()` для доступа к `cleaned_data`, чтобы избежать ошибок в случае, если поле отсутствует.

## Жизненный цикл обработки формы

1. **Создание экземпляра формы**
   ```python
   # С данными из запроса
   form = MyForm(request.POST, request.FILES)
   # Или пустая форма
   form = MyForm(initial={'name': 'Значение по умолчанию'})
   ```

2. **Проверка валидности**
   ```python
   if form.is_valid():
       # Форма валидна
   ```

3. **Доступ к данным**
   ```python
   # Валидные данные
   data = form.cleaned_data
   
   # Исходные данные (до валидации)
   raw_data = form.data
   ```

4. **Обработка ошибок**
   ```python
   if not form.is_valid():
       print(form.errors)  # Словарь ошибок
   ```

5. **Рендеринг формы в шаблоне**
   ```django
   <form method="post">
       {% csrf_token %}
       {{ form.as_p }}
       <button type="submit">Отправить</button>
   </form>
   ```

## Типы полей в Django Forms

| Название поля         | Описание                                                                 | Дополнительная информация                                                                 |
|-----------------------|-------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| CharField             | Поле для ввода текста произвольной длины. Самый распространенный тип поля в формах Django. | Поддерживает max_length, min_length, strip, empty_value.                                  |
| EmailField            | Поле для ввода email-адреса. Использует встроенные валидаторы для проверки формата электронной почты. | Наследуется от CharField, но проверяет формат с помощью validate_email.                  |
| URLField              | Поле для ввода URL-адресов. Проверяет корректность веб-адресов.          | Использует валидатор URLValidator для проверки корректности URL.                         |
| BooleanField          | Поле для булевых значений (True/False). По умолчанию обязательно для заполнения. | В HTML рендерится как чекбокс. Если не указано required=False, то должно быть отмечено.   |
| DateField             | Поле для ввода даты. Поддерживает различные форматы дат.                | Поддерживает настройку форматов через input_formats и может использовать календарь.      |
| IntegerField          | Поле для ввода целых чисел.                                              | Поддерживает min_value и max_value для ограничения диапазона.                           |
| DecimalField          | Поле для ввода десятичных чисел с фиксированной точностью.               | Требует указания max_digits и decimal_places.                                            |
| ChoiceField           | Поле с выбором из предопределенного списка значений.                     | Требует указания choices в виде списка кортежей [(value, label)].                        |
| MultipleChoiceField   | Поле для выбора нескольких значений из списка.                           | Возвращает список выбранных значений. Часто используется с CheckboxSelectMultiple.      |
| FileField             | Поле для загрузки файлов.                                                | Требует указания атрибута enctype="multipart/form-data" для формы.                      |
| ImageField            | Поле для загрузки изображений с валидацией типа файла.                  | Требует установки библиотеки Pillow для проверки, что файл является изображением.       |
| SlugField             | Специальное поле для slug-значений (URL-дружественных строк).           | Позволяет использовать буквы, цифры, подчеркивания и дефисы.                            |
| UUIDField             | Поле для UUID значений.                                                 | Проверяет, что введенное значение является корректным UUID.                              |
| ModelChoiceField      | Поле для выбора из объектов модели.                                      | Требует указания queryset для получения списка объектов модели.                          |
| ModelMultipleChoiceField | Поле для выбора нескольких объектов модели.                           | Возвращает QuerySet с выбранными объектами.                                              |

## Типы валидаторов в Django Forms

| Название валидатора               | Описание                                                                 | Пример использования                                                                 |
|-----------------------------------|-------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| validate_email                    | Проверяет корректность email-адреса согласно стандартам RFC.            | Автоматически используется в EmailField.                                           |
| URLValidator                      | Проверяет, что строка является корректным URL с указанным протоколом.   | Используется в URLField. Можно настраивать доступные схемы (http, https и т.д.).    |
| validate_slug                     | Проверяет, что строка является корректным slug (буквы, цифры, _, -).    | Используется в SlugField для проверки URL-дружественных строк.                    |
| MinValueValidator                 | Проверяет, что значение больше или равно указанному минимуму.           | `IntegerField(validators=[MinValueValidator(10)])`                                |
| MaxValueValidator                 | Проверяет, что значение меньше или равно указанному максимуму.          | `IntegerField(validators=[MaxValueValidator(100)])`                               |
| MinLengthValidator                | Проверяет, что строка имеет минимальную длину.                          | `CharField(validators=[MinLengthValidator(5)])`                                  |
| MaxLengthValidator                | Проверяет, что строка не превышает максимальную длину.                  | `CharField(validators=[MaxLengthValidator(50)])`                                 |
| ProhibitNullCharactersValidator   | Запрещает использование null-символов в строке (защита от инъекций).    | `CharField(validators=[ProhibitNullCharactersValidator()])`                       |
| StepValueValidator                | Проверяет, что значение кратно указанному шагу.                         | `IntegerField(validators=[StepValueValidator(5)])`                               |
| RegexValidator                    | Проверяет соответствие строки регулярному выражению.                    | `CharField(validators=[RegexValidator(regex='^[a-z]+$')])`                       |
| FileExtensionValidator            | Проверяет расширение загружаемого файла.                                | `FileField(validators=[FileExtensionValidator(['pdf', 'doc', 'docx'])])`         |
| validate_integer                  | Проверяет, что значение является целым числом.                          | Автоматически используется в IntegerField.                                        |

## Типы атрибутов в Django Forms

| Название атрибута     | Описание                                                                 | Пример использования                                                                 |
|-----------------------|-------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| required              | Указывает, является ли поле обязательным для заполнения.                 | `forms.CharField(required=True)` или `required=False`                             |
| label                 | Устанавливает человекочитаемую метку для поля в форме.                   | `forms.CharField(label="Ваше полное имя")`                                        |
| initial               | Устанавливает начальное значение для поля.                               | `forms.CharField(initial="Значение по умолчанию")`                               |
| help_text             | Текст-подсказка, отображаемый рядом с полем для пояснения.               | `forms.EmailField(help_text="Введите действующий email-адрес.")`                  |
| widget                | Указывает виджет (HTML-элемент), который будет использоваться для поля.   | `forms.CharField(widget=forms.Textarea)`                                          |
| error_messages        | Словарь с сообщениями об ошибках для разных типов валидации.             | `forms.CharField(error_messages={'required': 'Поле обязательно для заполнения'})`  |
| validators            | Список валидаторов, которые будут применены к значению поля.             | `forms.CharField(validators=[MinLengthValidator(5)])`                             |
| localize             | Указывает, должно ли поле быть локализовано (например, формат даты).     | `forms.DateField(localize=True)`                                                  |
| disabled             | Отключает поле, делая его доступным только для чтения.                    | `forms.CharField(disabled=True)`                                                  |
| label_suffix         | Задает символ, который будет добавлен после метки поля.                   | `forms.CharField(label_suffix=":")`                                               |
| max_length           | Устанавливает максимальную длину для CharField.                           | `forms.CharField(max_length=100)`                                                |
| min_length           | Устанавливает минимальную длину для CharField.                            | `forms.CharField(min_length=5)`                                                  |
| empty_value          | Значение, которое будет использоваться вместо пустой строки.              | `forms.CharField(empty_value=None)`                                              |

## Типы виджетов в Django Forms

| Название виджета      | Описание                                                                 | Пример использования                                                                 |
|-----------------------|-------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| TextInput             | Стандартный однострочный текстовый ввод (`<input type="text">`).         | `forms.CharField(widget=forms.TextInput(attrs={"class": "input-field"}))`          |
| Textarea              | Многострочное текстовое поле (`<textarea>`).                             | `forms.CharField(widget=forms.Textarea(attrs={"rows": 5, "cols": 40}))`           |
| NumberInput           | Поле для ввода чисел (`<input type="number">`).                           | `forms.IntegerField(widget=forms.NumberInput(attrs={"step": "1"}))`               |
| EmailInput            | Поле для ввода email (`<input type="email">`).                           | `forms.EmailField(widget=forms.EmailInput(attrs={"autocomplete": "email"}))`      |
| URLInput              | Поле для ввода URL (`<input type="url">`).                               | `forms.URLField(widget=forms.URLInput)`                                            |
| PasswordInput         | Поле для ввода пароля (`<input type="password">`).                       | `forms.CharField(widget=forms.PasswordInput(render_value=False))`                 |
| HiddenInput           | Скрытое поле (`<input type="hidden">`).                                   | `forms.CharField(widget=forms.HiddenInput)`                                        |
| DateInput             | Поле для выбора даты (`<input type="date">`).                            | `forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))`                |
| DateTimeInput         | Поле для выбора даты и времени.                                          | `forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type": "datetime-local"}))` |
| TimeInput             | Поле для выбора времени (`<input type="time">`).                         | `forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}))`                |
| CheckboxInput         | Чекбокс (`<input type="checkbox">`).                                     | `forms.BooleanField(widget=forms.CheckboxInput)`                                  |
| Select                | Выпадающий список (`<select>`).                                          | `forms.ChoiceField(widget=forms.Select, choices=CHOICES)`                          |
| SelectMultiple        | Выпадающий список с множественным выбором.                               | `forms.MultipleChoiceField(widget=forms.SelectMultiple, choices=CHOICES)`          |
| RadioSelect           | Группа радиокнопок (`<input type="radio">`).                             | `forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)`                     |
| CheckboxSelectMultiple| Группа чекбоксов для множественного выбора.                              | `forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=CHOICES)`  |
| FileInput             | Поле для загрузки файлов (`<input type="file">`).                        | `forms.FileField(widget=forms.FileInput)`                                          |
| ClearableFileInput    | Поле для загрузки файлов с возможностью очистки.                         | `forms.FileField(widget=forms.ClearableFileInput)`                                 |
| SelectDateWidget      | Комбинированный виджет для выбора даты (три выпадающих списка).          | `forms.DateField(widget=forms.SelectDateWidget(years=range(2020, 2026)))`         |
| SplitDateTimeWidget   | Комбинированный виджет для выбора даты и времени (два поля).             | `forms.DateTimeField(widget=forms.SplitDateTimeWidget)`                           |

## Полезные методы форм

| Название метода       | Описание                                                                 | Пример использования                                                                 |
|-----------------------|-------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| as_p                  | Рендерит форму, оборачивая каждое поле в тег `<p>`.                      | `{{ form.as_p }}` в шаблоне Django                                                  |
| as_ul                 | Рендерит форму как список элементов `<li>` (без тегов `<ul>`).           | `{{ form.as_ul }}` в шаблоне Django                                                 |
| as_table              | Рендерит форму как строки таблицы `<tr>` (без тегов `<table>`).          | `{{ form.as_table }}` в шаблоне Django                                              |
| as_div                | Рендерит форму, оборачивая каждое поле в тег `<div>`.                    | `{{ form.as_div }}` в шаблоне Django                                                |
| is_valid              | Проверяет валидность данных формы.                                       | `if form.is_valid(): ...`                                                           |
| clean                 | Метод для общей валидации полей формы.                                   | Переопределяется в подклассах для кастомной валидации                                |
| clean_<fieldname>     | Методы для валидации отдельных полей.                                    | `def clean_email(self): ...`                                                        |
| has_changed           | Проверяет, изменились ли данные формы по сравнению с начальными.        | `if form.has_changed(): ...`                                                        |
| add_error             | Добавляет ошибку для конкретного поля или в общие ошибки формы.          | `form.add_error('email', 'Некорректный email')`                                    |