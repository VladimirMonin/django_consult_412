# Тема Django. Корпоративный блог. Пагинатор. Детальное представление.  Урок 67

## Объект Paginator


В Django пагинация реализована с помощью класса `Paginator`, который позволяет разбивать большой набор данных на страницы.

Импорт класса:
```python
from django.core.paginator import Paginator
```


Создание объекта Paginator:
```python
paginator = Paginator(queryset, per_page)
```


- `queryset` — набор данных, который нужно разбить на страницы.
- `per_page` — количество элементов на странице.

Данные по номеру страницы передаются через параметр `page` в URL.
`/blog/?page=2`

Формат функционального представления:

```python
def blog_list(request):
    page_number = request.GET.get('page')
    queryset = Post.objects.all()
    paginator = Paginator(queryset, per_page)
    page = paginator.get_page(page_number)
    return render(request, 'blog/blog_list.html', {'page': page})
```

Однако классовая view `ListView` уже содержит в себе пагинацию. Нужно лишь добавить атрибут `paginate_by` в класс `ListView`.

## Объекты `paginator` и `page_obj` в шаблоне

### Свойства `paginator` (`django.core.paginator.Paginator`)
- `paginator.count` — общее количество элементов.
- `paginator.num_pages` — общее количество страниц.
- `paginator.page_range` — диапазон номеров страниц.

### Свойства `page_obj` (`django.core.paginator.Page`)
- `page_obj.object_list` — список объектов на текущей странице.
- `page_obj.number` — номер текущей страницы.
- `page_obj.paginator` — связанный объект `Paginator`.
- `page_obj.has_next` — есть ли следующая страница.
- `page_obj.has_previous` — есть ли предыдущая страница.
- `page_obj.next_page_number` — номер следующей страницы.
- `page_obj.previous_page_number` — номер предыдущей страницы.
- `page_obj.start_index` — индекс первого элемента на странице.
- `page_obj.end_index` — индекс последнего элемента на странице.
- `page_obj.has_other_pages` — есть ли другие страницы.

Простой пример цикла шаблонизатора для отрисовки кнопок пагинации
по маршруту `/blog/`
Проверяем что страниц больше 1 страницы, и если это так, сделать максимально простой цикл.

```html
{% if page_obj.has_other_pages %}
        {% for page in page_obj.paginator.page_range %}
            <a href="?page={{ page }}">{{ page }}</a>
        {% endfor %}
{% endif %}
```
