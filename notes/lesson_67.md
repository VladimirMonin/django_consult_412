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

### Простой пример шаблона пагинации

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

### Чуть более сложный пример шаблона пагинации
```html
{% if page_obj.has_other_pages %}
    <div class="paginator">
    <nav>
        <ul class="pagination pagination-lg justify-content-center">
        {% for page in page_obj.paginator.page_range %}
            {% comment %} Проверяем является ли страница текущей {% endcomment %}
            {% if page == page_obj.number %}
            <li class="page-item active" aria-current="page">
                <span class="page-link">{{ page }}</span>
            </li>
            {% else %}
            <li class="page-item">
                <a class="page-link" href="?page={{ page }}">{{ page }}</a>
            </li>
            {% endif %}
        {% endfor %}
        </ul>
    </nav>
    </div>
    {% endif %}
```

### Проблемы с пагинацией и поисковой выдачей

пагинация для списка заказов - есть пробелма - поиск сбрасывается при переходе между страницами поисковой выдачи

` <a class="page-link" href="?{% if request.GET %}{{ request.GET.urlencode }}&{% endif %}page={{ page }}">{{ page }}</a>`

- Это решение проблемы! Рассказать как это работает.




============


Фрагмент-кэш в Django (тег {% cache ... %}) сохраняет только сгенерированный HTML, а не сами объекты модели и не результаты SQL-запросов, которые выполняются ДО рендеринга шаблона.

Что происходит у вас:

View формирует queryset Post (и связанные объекты), выполняя все необходимые SELECT’ы.
Шаблон posts_list.html перебирает queryset:
{% for post in posts %}
    {% include "blog/post_card_include.html" %}
{% endfor %}

txt


→ На этом этапе объекты post уже извлечены из БД, следовательно SQL-запросы уже выполнены и Debug Toolbar их показывает.
Далее вступает в работу тег {% cache 10 post.id %} внутри post_card_include.html.
Если фрагмент найден в кеше, Django просто подставит сохранённый HTML и НЕ будет заново вычислять выражения внутри тега. Поэтому: • Внутри кэшируемого блока «лайки»/«комментарии» выражение post.likes.count больше не вызывается → дополнительных SQL нет — вы это и наблюдаете.
• Но это НЕ отменяет тех запросов, которые уже произошли, чтобы получить сам объект post, post.cover, post.tags.all и т.д.
Иными словами, кэш шаблона сокращает время рендеринга, но не уменьшает число запросов, необходимых для формирования контекста.

Как уменьшить число SQL-запросов:
• Использовать кэш всего представления (@cache_page(...)) — тогда при повторном обращении Django не будет заходить в view и, следовательно, не выполнит вообще никаких SQL.

• Или кэшировать данные, а не шаблон: сохранять уже сформированные словари/списки постов в Redis/Memcached и отдавать их из кеша.

• Либо оптимизировать queryset с помощью select_related, prefetch_related, annotate и т.п., чтобы минимизировать количество выполняемых запросов.

Вывод: фрагмент-кэш правильный, но он решает другую задачу (ускорение HTML-рендера). Если цель — «обнулить» SQL-запросы при повторных обращениях, применяйте кэш всего view или кэшируйте данные, а не только шаблон.


Фрагмент-кэш в Django (тег {% cache ... %}) сохраняет только сгенерированный HTML, а не сами объекты модели и не результаты SQL-запросов, которые выполняются ДО рендеринга шаблона.

Что происходит у вас:

View формирует queryset Post (и связанные объекты), выполняя все необходимые SELECT’ы.
Шаблон posts_list.html перебирает queryset:
{% for post in posts %}
    {% include "blog/post_card_include.html" %}
{% endfor %}

txt


→ На этом этапе объекты post уже извлечены из БД, следовательно SQL-запросы уже выполнены и Debug Toolbar их показывает.
Далее вступает в работу тег {% cache 10 post.id %} внутри post_card_include.html.
Если фрагмент найден в кеше, Django просто подставит сохранённый HTML и НЕ будет заново вычислять выражения внутри тега. Поэтому: • Внутри кэшируемого блока «лайки»/«комментарии» выражение post.likes.count больше не вызывается → дополнительных SQL нет — вы это и наблюдаете.
• Но это НЕ отменяет тех запросов, которые уже произошли, чтобы получить сам объект post, post.cover, post.tags.all и т.д.
Иными словами, кэш шаблона сокращает время рендеринга, но не уменьшает число запросов, необходимых для формирования контекста.

Как уменьшить число SQL-запросов:
• Использовать кэш всего представления (@cache_page(...)) — тогда при повторном обращении Django не будет заходить в view и, следовательно, не выполнит вообще никаких SQL.

• Или кэшировать данные, а не шаблон: сохранять уже сформированные словари/списки постов в Redis/Memcached и отдавать их из кеша.

• Либо оптимизировать queryset с помощью select_related, prefetch_related, annotate и т.п., чтобы минимизировать количество выполняемых запросов.

Вывод: фрагмент-кэш правильный, но он решает другую задачу (ускорение HTML-рендера). Если цель — «обнулить» SQL-запросы при повторных обращениях, применяйте кэш всего view или кэшируйте данные, а не только шаблон.


`@cache_page` — это декоратор из `django.views.decorators.cache`, который сохраняет
полностью сгенерированный HTTP-ответ во фронтовом бекенде кеша (Memcached, Redis, файл и т. д.).
При повторном запросе к тому же URL Django даже не заходит во view — сразу отдаётся
скопированный ответ, поэтому БД не трогается, шаблоны не рендерятся, middleware не работают
(кроме тех, что идут ДО кеширования: `UpdateCacheMiddleware`/`FetchFromCacheMiddleware`
и `CacheMiddleware`).

Сигнатура  

```python
django.views.decorators.cache.cache_page(timeout, *, cache=None, key_prefix=None)
```

• `timeout` — время жизни объекта (секунды).  
• `cache` — имя backend’а из `CACHES` (по умолчанию `default`).  
• `key_prefix` — строка, добавляемая к началу ключа (удобно инвалидировать группу ответов).

--------------------------------------------------------------------
1. Применение к функциональному представлению (FBV)
--------------------------------------------------------------------

```python
from django.views.decorators.cache import cache_page
from django.shortcuts import render

@cache_page(60 * 15)            # 15 минут
def posts_list(request):
    qs = Post.objects.select_related('author').prefetch_related('tags')
    return render(request, 'blog/posts_list.html', {'posts': qs})
```

• Для каждого уникального URL формируется ключ  
  `VIEW_PREFIX + KEY_PREFIX + URL + QUERY_STRING`.  
• Если к view обращаются разные пользователи, но страница одинаковая для всех,
  этого достаточно.  
• Если нужен кеш «на пользователя», используют `@vary_on_cookie` или вручную
  добавляют идентификатор пользователя к `key_prefix`.

--------------------------------------------------------------------
2. Применение к классовому представлению (CBV)
--------------------------------------------------------------------

Для CBV используют `method_decorator`, потому что нужно обернуть конкретный
HTTP-метод (`get`, иногда `dispatch`).

```python
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.decorators.cache import cache_page

@method_decorator(cache_page(60 * 30), name='dispatch')        # кеш на все методы
class PostListView(ListView):
    model = Post
    template_name = 'blog/posts_list.html'
    queryset = (Post.objects
                      .select_related('author')
                      .prefetch_related('tags')
               )
```

Альтернативно — только `get`:

```python
class PostListView(ListView):
    model = Post
    template_name = 'blog/posts_list.html'

    @method_decorator(cache_page(60 * 5))
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)
```

--------------------------------------------------------------------
3. Комбинации и дополнительные нюансы
--------------------------------------------------------------------

1. **Отдельный backend**  
   Если список постов должен жить в Redis, а остальное — в Memcached:

   ```python
   @cache_page(300, cache='redis')
   def posts_list(request): ...
   ```

2. **Групповая инвалидция через `key_prefix`**  
   При публикации нового поста сбрасываем всё:

   ```python
   @cache_page(600, key_prefix='posts_page')
   def posts_list(request): ...
   ```

   В админке после сохранения поста:

   ```python
   from django.core.cache import caches
   caches['default'].clear()                # или delete_pattern('*posts_page*')
   ```

3. **Vary-заголовки**  
   Если контент зависит от куки или Accept-Language:

   ```python
   from django.views.decorators.vary import vary_on_cookie, vary_on_headers

   @vary_on_cookie
   @cache_page(600)
   def dashboard(request): ...
   ```

4. **CacheMiddleware**  
   Вместо точечных декораторов можно вставить «site-wide» кеширование:

   ```python
   MIDDLEWARE = [
       'django.middleware.cache.UpdateCacheMiddleware',
       'django.middleware.common.CommonMiddleware',
       'django.middleware.cache.FetchFromCacheMiddleware',
       ...
   ]
   CACHE_MIDDLEWARE_ALIAS = 'default'
   CACHE_MIDDLEWARE_SECONDS = 60 * 10
   CACHE_MIDDLEWARE_KEY_PREFIX = ''
   ```

   Тогда кешируется всё, кроме URL, отмеченных `never_cache` или хэдером
   `Cache-Control: no-cache`.

--------------------------------------------------------------------
4. Когда что выбирать
--------------------------------------------------------------------
• **@cache_page** на функцию/класс — самый быстрый способ точечно убрать нагрузку
   с тяжёлых страниц (списки, детальные отчёты).  
• **Фрагмент-кэш** (`{% cache %}` в шаблоне) — если нужно кешировать
   часть страницы, но остальное (личные данные, csrf-токены) должно остаться динамичным.  
• **Middleware-кэш** — когда сайт почти весь статичен для анонимов
   (например, блог без личных кабинетов).  
• **Низкоуровневый кеш** (`cache.get/set`) — для кеширования сложных вычислений,
   sql-агрегаций, API-запросов и т. д.

--------------------------------------------------------------------
Мини-шпаргалка
--------------------------------------------------------------------
```text
FBV:           @cache_page(900)
CBV (all):     @method_decorator(cache_page(900), name='dispatch')
CBV (GET):     @method_decorator(cache_page(900), name='get')
Custom cache:  @cache_page(900, cache='fast-redis', key_prefix='posts')
Disable:       @never_cache    # для админки, форм и т. п.
```

Так вы сможете гибко выбирать уровень кеширования и уменьшать нагрузку
как на базу данных, так и на процесс рендеринга.


