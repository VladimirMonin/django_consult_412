from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import Post

class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Post.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        # Вручную строим URL, чтобы не зависеть от get_absolute_url
        # Это может быть не идеально, если структура URL изменится,
        # но это решает проблему 500 без добавления нового кода.
        return f'/blog/{obj.slug}/'

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return ['landing', 'about_us', 'services_list']

    def location(self, item):
        return reverse(item)
