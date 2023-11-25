from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=150, verbose_name="Название категории")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"  # Единственное число
        verbose_name_plural = "Категории"  # Множественное число


class Article(models.Model):
    title = models.CharField(verbose_name="Заголовок статьи", max_length=155, unique=True)
    short_description = models.TextField(verbose_name="Краткое описание", max_length=255)
    full_description = models.TextField(verbose_name="Полное описание")
    photo = models.ImageField(verbose_name="Фото", upload_to="photos/articles/")
    views = models.IntegerField(verbose_name="Количество просмотров", default=0)
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Дата обновления", auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор", related_name="articles")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория", related_name="articles")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'article_id': self.pk})

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ['-created_at']


class ArticleCountView(models.Model):
    session_id = models.CharField(max_length=150)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, blank=True, null=True)


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    body = models.TextField()


class Like(models.Model):
    user = models.ManyToManyField(User, related_name="likes")
    article = models.OneToOneField(Article,
                                   on_delete=models.CASCADE,
                                   blank=True,
                                   null=True, related_name="likes")
    comment = models.OneToOneField(Comment,
                                   on_delete=models.CASCADE,
                                   blank=True,
                                   null=True, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Dislike(models.Model):
    user = models.ManyToManyField(User, related_name="dislikes")
    article = models.OneToOneField(Article,
                                   on_delete=models.CASCADE,
                                   blank=True,
                                   null=True, related_name="dislikes")
    comment = models.OneToOneField(Comment,
                                   on_delete=models.CASCADE,
                                   blank=True,
                                   null=True, related_name="dislikes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FavoriteArticle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="favorites")

    def __str__(self):
        return f'{self.user}: {self.article}'
