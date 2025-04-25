# Django Forms: Поля, Валидаторы, Атрибуты и Виджеты

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