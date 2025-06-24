from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from unidecode import unidecode
from markdown import markdown
from django.core.exceptions import ValidationError

USER_MODEL = get_user_model()


class Category(models.Model):
    """Модель категории."""

    name = models.CharField(max_length=200, verbose_name="Название")
    cover = models.ImageField(
        upload_to="categories/", verbose_name="Обложка", blank=True, null=True
    )
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(unique=True, verbose_name="Слаг", blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Используем стороннюю библиотеку unicode + slugify
            ascii_name = unidecode(self.name)  # Транслитерация
            self.slug = slugify(ascii_name)  # Генерация slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="Слаг", blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Используем стороннюю библиотеку unicode + slugify
            ascii_name = unidecode(self.name)  # Транслитерация
            self.slug = slugify(ascii_name)  # Генерация slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Post(models.Model):
    """Модель поста."""

    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(unique=True, verbose_name="Слаг", blank=True)
    cover = models.ImageField(
        upload_to="posts/", verbose_name="Обложка", blank=True, null=True
    )
    md_content = models.TextField(verbose_name="Содержание (Markdown)", blank=True)
    html_content = models.TextField(verbose_name="Содержание (HTML)", blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория",
        related_name="posts",
    )
    tags = models.ManyToManyField(
        Tag, verbose_name="Теги", blank=True, related_name="posts"
    )
    author = models.ForeignKey(
        USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Автор",
        related_name="posts",
    )
    likes = models.ManyToManyField(
        USER_MODEL, verbose_name="Лайки", blank=True, related_name="liked_posts"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_published = models.BooleanField(default=False, verbose_name="Опубликован")
    views_count = models.PositiveIntegerField(
        default=0, verbose_name="Количество просмотров"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            # Используем стороннюю библиотеку unicode + slugify
            ascii_title = unidecode(self.title)  # Транслитерация
            self.slug = slugify(ascii_title)  # Генерация slug
            self.html_content = markdown(self.md_content)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-created_at"]


class Comment(models.Model):
    """Модель комментария."""

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, verbose_name="Пост", related_name="comments"
    )
    author = models.ForeignKey(
        USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Автор",
        related_name="comments",
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Родительский комментарий",
        related_name="replies",
    )

    text = models.TextField(verbose_name="Текст")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_published = models.BooleanField(default=False, verbose_name="Опубликован")
    likes = models.ManyToManyField(
        USER_MODEL, verbose_name="Лайки", blank=True, related_name="liked_comments"
    )

    def get_first_parent_pk(self):
        """
        Метод который можно вызывать в шаблоне при ответе на комментарий
        Чтобы безопасно и быстро получить родительский комментарий верхнего уровня
        """
        if self.parent:
            return self.parent.pk
        return self.pk

    def clean(self):
        """Проверка уровня вложенности"""
        if self.parent:
            if self.parent.parent:
                raise ValidationError("Допускается только один уровень вложенности комментариев")

    def __str__(self):
        return f"Комментарий к посту {self.post.title}"

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["-created_at"]
