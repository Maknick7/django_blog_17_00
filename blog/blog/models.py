from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.

# blog_category


class Category(models.Model):
    title = models.CharField("Название категории", max_length=150)

    def get_absolute_url(self):
        return reverse("category_articles", kwargs={"pk": self.pk})

    def __str__(self):
        return self.title


class Article(models.Model):
    title = models.CharField("Название статьи", max_length=150, unique=True)
    content = models.TextField("Описание статьи")
    image = models.ImageField(verbose_name="Фотография", upload_to="photos/", blank=True, null=True)
    views = models.IntegerField(verbose_name="Количество просмотров", default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.title


# article.comments.all
# article.comment_set.all
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content


class ArticleCountView(models.Model):
    session_id = models.CharField(max_length=150, null=True, blank=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, default=None, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True, blank=True)


# article.likes.all

class Like(models.Model):
    user = models.ManyToManyField(User, related_name="likes")
    article = models.OneToOneField(Article, related_name="likes", on_delete=models.CASCADE, null=True, blank=True)
    comment = models.OneToOneField(Comment, related_name="likes", on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.article)


class Dislike(models.Model):
    user = models.ManyToManyField(User, related_name="dislikes")
    article = models.OneToOneField(Article, related_name="dislikes", on_delete=models.CASCADE, null=True, blank=True)
    comment = models.OneToOneField(Comment, related_name="dislikes", on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.article)