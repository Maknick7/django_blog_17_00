from django import template

from web_site.models import Category, FavoriteArticle

register = template.Library()


@register.simple_tag()
def get_categories():
    categories = Category.objects.all()
    return categories

@register.simple_tag()
def is_article_in_user_favorites(user, article):
    obj = FavoriteArticle.objects.filter(user=user, article=article).first()
    if obj is None:
        return False
    return True