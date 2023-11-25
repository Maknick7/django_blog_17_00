from django.urls import path

from . import views


urlpatterns = [
    # path('', views.home_view, name='home'),
    path('', views.HomeListView.as_view(), name='home'),
    path('search/', views.SearchResults.as_view(), name='search'),
    path('categories/<str:category_id>/', views.category_articles, name='category_articles'),
    path('articles/<str:article_id>/', views.article_detail, name="article_detail"),

    path('login/', views.login_view, name="login"),
    path('registration/', views.registration_view, name="registration"),
    path('logout/', views.user_logout, name='logout'),

    path('article/create/', views.create_article, name='create'),
    path('article/delete/<str:pk>/', views.ArticleDeleteView.as_view(), name='delete'),
    path('article/update/<str:pk>/', views.ArticleUpdateView.as_view(), name='update'),

    path('profile/<str:username>/', views.profile_view, name="profile"),
    path('profile/<str:username>/favorites/', views.user_favorites, name="user_favorites"),

    path('<str:obj_type>/<int:obj_id>/<str:action>/', views.add_like_or_dislike, name='add_vote'),

    path('about/', views.about_author_view, name="about"),

    path('<int:user_id>/favorites/add/<int:article_id>/', views.add_to_favorites, name="add_fav"),
    path('<int:user_id>/favorites/delete/<int:article_id>/', views.delete_from_favorites, name="del_fav"),
]


"""
Создать страницу "Об авторе"
сделать функцию для перехода на эту страницу
создать ссылку для перехода на эту страницу
"""