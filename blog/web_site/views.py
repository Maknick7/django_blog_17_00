from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import DeleteView, UpdateView, ListView

from .forms import LoginForm, RegistrationForm, ArticleForm, CommentForm
from .models import Article, Category, Comment, ArticleCountView, Like, Dislike, FavoriteArticle


class ArticleUpdateView(UpdateView):
    model = Article
    template_name = "web_site/article_form.html"
    form_class = ArticleForm
    # success_url = '/'


class ArticleDeleteView(DeleteView):
    model = Article
    template_name = 'web_site/article_confirm_delete.html'
    success_url = '/'


class HomeListView(ListView):
    model = Article
    template_name = "web_site/index.html"
    context_object_name = "articles"
    paginate_by = 3

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        articles = paginator.get_page(page)
        context['articles'] = articles
        return context


class SearchResults(HomeListView):
    paginate_by = 1000000000000

    def get_queryset(self):
        query = self.request.GET.get('q')
        return Article.objects.filter(
            Q(title__iregex=query) | Q(short_description__iregex=query)
        )


def home_view(request):
    articles = Article.objects.all()
    paginator = Paginator(articles, 3)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    context = {
        "articles": articles
    }
    return render(request, 'web_site/index.html', context)


def category_articles(request, category_id):
    category = Category.objects.get(pk=category_id)
    articles = category.articles.all()
    context = {
        "articles": articles
    }
    return render(request, 'web_site/index.html', context)


def article_detail(request, article_id):
    article = Article.objects.get(pk=article_id)

    try:
        article.likes
    except Exception as e:
        print(e, e.__class__)
        Like.objects.create(article=article)

    try:
        article.dislikes
    except Exception as e:
        print(e, e.__class__)
        Dislike.objects.create(article=article)

    if not request.session.session_key:
        request.session.save()

    session_key = request.session.session_key

    viewed_items = ArticleCountView.objects.filter(
        article=article,
        session_id=session_key
    )

    if viewed_items.count() == 0 and str(session_key) != "None":
        viewed = ArticleCountView()
        viewed.article = article
        viewed.session_id = session_key
        viewed.save()

        article.views += 1
        article.save()

    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.article = article
            form.author = request.user
            form.save()

            try:
                form.likes
            except Exception as e:
                Like.objects.create(comment=form)

            try:
                form.dislikes
            except Exception as e:
                Dislike.objects.create(comment=form)

            return redirect('article_detail', article.pk)
    else:
        form = CommentForm()

    comments = article.comment_set.all()

    likes = article.likes.user.all().count()
    dislikes = article.dislikes.user.all().count()

    comments_likes = {
        comment.pk: comment.likes.user.all().count()
        for comment in comments
    }

    comments_dislikes = {
        comment.pk: comment.dislikes.user.all().count()
        for comment in comments
    }

    context = {
        "article": article,
        "form": form,
        "comments": comments,
        "likes": likes,
        "dislikes": dislikes,
        "comments_likes": comments_likes,
        "comments_dislikes": comments_dislikes,
    }
    return render(request, "web_site/article_detail.html", context)


def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
    else:
        form = LoginForm()
    context = {
        "form": form
    }
    return render(request, "web_site/login.html", context)


def registration_view(request):
    if request.method == "POST":
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    context = {
        "form": form
    }
    return render(request, "web_site/registration.html", context)


def user_logout(request):
    logout(request)
    return redirect('home')


def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.save()
            return redirect('article_detail', form.pk)
    else:
        form = ArticleForm()

    context = {
        'form': form
    }

    return render(request, 'web_site/article_form.html', context)


def profile_view(request, username):
    from datetime import datetime

    user = User.objects.filter(username=username).first()
    now_day = datetime.now().date()
    joined_day = user.date_joined.date()
    total = now_day - joined_day

    articles = Article.objects.filter(author=user)
    total_views = sum([article.views for article in articles])
    total_comments = sum([article.comment_set.all().count() for article in articles])
    print(total_comments)

    context = {
        'user': user,
        'experience': total.days,
        'total_views': total_views,
        'total_comments': total_comments,
        'articles': articles
    }
    return render(request, "web_site/profile.html", context)


def add_like_or_dislike(request, obj_type, obj_id, action):
    from django.shortcuts import get_object_or_404
    # obj_type == Article
    # obj_type == Comment

    obj = None

    if obj_type == 'article':
        obj = get_object_or_404(Article, pk=obj_id)
    elif obj_type == 'comment':
        obj = get_object_or_404(Comment, pk=obj_id)

    try:
        obj.likes
    except Exception as e:
        if obj.__class__ is Article:
            Like.objects.create(article=obj)
        else:
            Like.objects.create(comment=obj)

    try:
        obj.dislikes
    except Exception as e:
        if obj.__class__ is Article:
            Dislike.objects.create(article=obj)
        else:
            Dislike.objects.create(comment=obj)

    # add_like
    # add_dislike

    if action == 'add_like':
        if request.user in obj.likes.user.all():  # проверяем ставил ли пользователь лайк
            obj.likes.user.remove(request.user.pk)  # удаляем лайк, если он его уже поставил
        else:  # если лайк не был добавлен
            obj.likes.user.add(request.user.pk)  # добавляем лайк
            obj.dislikes.user.remove(request.user.pk)  # удаляем дизлайк

    elif action == 'add_dislike':
        if request.user in obj.dislikes.user.all():  # проверяем ставил ли пользователь дизлайк
            obj.dislikes.user.remove(request.user.pk)  # удаляем дизлайк, если он его уже поставил
        else:  # если дизлайк не был добавлен
            obj.dislikes.user.add(request.user.pk)  # добавляем дизлайк
            obj.likes.user.remove(request.user.pk)  # удаляем дизлайк
    else:
        return redirect(request.environ['HTTP_REFERER'])
    return redirect(request.environ['HTTP_REFERER'])


def user_favorites(request, username):
    user = User.objects.get(username=username)
    favorites = FavoriteArticle.objects.filter(user=user)
    articles = [fav.article for fav in favorites]
    context = {
        "articles": articles
    }
    return render(request, "web_site/favorites.html", context)


def add_to_favorites(request, user_id, article_id):
    user = User.objects.filter(pk=user_id).first()
    article = Article.objects.filter(pk=article_id).first()
    obj = FavoriteArticle.objects.create(
        user=user,
        article=article
    )
    obj.save()
    return redirect(request.environ["HTTP_REFERER"])


def delete_from_favorites(request, user_id, article_id):
    user = User.objects.filter(pk=user_id).first()
    article = Article.objects.filter(pk=article_id).first()
    obj = FavoriteArticle.objects.get(
        user=user,
        article=article
    )
    obj.delete()
    return redirect(request.environ["HTTP_REFERER"])


def about_author_view(request):
    return render(request, "web_site/about_author.html")
