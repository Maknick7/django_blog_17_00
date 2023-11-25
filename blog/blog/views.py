from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import UpdateView, DeleteView, ListView

from .forms import LoginForm, RegistrationForm, ArticleForm, CommentForm
from .models import Article, Category, ArticleCountView, Like, Dislike, Comment
from django.utils.datetime_safe import datetime


class HomeListView(ListView):
    model = Article
    template_name = "pages/index.html"
    context_object_name = "articles"


class SearchResults(HomeListView):
    def get_queryset(self):
        query = self.request.GET.get("q")
        return Article.objects.filter(
            # title__icontains=query,
            Q(title__iregex=query) | Q(content__iregex=query)
        )


# Create your views here.

class UpdateArticleView(UpdateView):
    template_name = "pages/article_form.html"
    form_class = ArticleForm
    model = Article
    success_url = "/"


class DeleteArticleView(DeleteView):
    model = Article
    success_url = "/"
    template_name = "pages/article_confirm_delete.html"


def home_view(request):
    articles = Article.objects.all()
    context = {
        "articles": articles
    }
    return render(request, "pages/index.html", context)


def category_articles(request, pk):
    category = Category.objects.get(pk=pk)  # fetchone
    articles = Article.objects.filter(category=category)  # fetchall
    context = {
        "articles": articles,
        "pk": pk
    }
    return render(request, "pages/index.html", context)


def add_vote(request, obj_type, obj_id, action):
    # print(request.environ["HTTP_REFERER"])
    obj = None
    if obj_type == "article":
        obj = get_object_or_404(Article, pk=obj_id)
    elif obj_type == "comment":
        obj = get_object_or_404(Comment, pk=obj_id)

    try:
        obj.dislikes
    except Exception as e:
        if obj.__class__ is Article:
            Dislike.objects.create(article=obj)
        else:
            Dislike.objects.create(comment=obj)

    try:
        obj.likes
    except Exception as e:
        if obj.__class__ is Article:
            Like.objects.create(article=obj)
        else:
            Like.objects.create(comment=obj)

    if action == "add_like":
        if request.user in obj.likes.user.all():
            obj.likes.user.remove(request.user.pk)
        else:
            obj.likes.user.add(request.user.pk)
            obj.dislikes.user.remove(request.user.pk)
    elif action == "add_dislike":
        if request.user in obj.dislikes.user.all():
            obj.dislikes.user.remove(request.user.pk)
        else:
            obj.dislikes.user.add(request.user.pk)
            obj.likes.user.remove(request.user.pk)
    else:
        return redirect(request.environ["HTTP_REFERER"])
    return redirect(request.environ["HTTP_REFERER"])


def article_detail(request, pk):
    article = Article.objects.get(pk=pk)
    comments = article.comments.all()

    try:
        article.dislikes
    except Exception as e:
        print(e)
        Dislike.objects.create(article=article)

    try:
        article.likes
    except Exception as e:
        print(e)
        Like.objects.create(article=article)

    likes_count = article.likes.user.all().count()
    dislikes_count = article.dislikes.user.all().count()
    comments_likes_count = {
        comment.pk: comment.likes.user.all().count()
        for comment in comments
    }
    comments_dislikes_count = {
        comment.pk: comment.dislikes.user.all().count()
        for comment in comments
    }

    if not request.session.session_key:
        request.session.save()

    session_id = request.session.session_key
    if not request.user.is_authenticated:
        views_items = ArticleCountView.objects.filter(session_id=session_id, article=article)
        if not views_items.count() and str(session_id) != "None":
            views = ArticleCountView()
            views.article = article
            views.session_id = session_id
            views.save()

            article.views += 1
            article.save()
    else:
        views_items = ArticleCountView.objects.filter(article=article, user=request.user)

        if not views_items.count():
            views = ArticleCountView()
            views.article = article
            views.user = request.user
            views.save()

            article.views += 1
            article.save()

    if request.method == "POST":
        form = CommentForm(data=request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.article = article
            form.save()

            try:
                form.dislikes
            except Exception as e:
                print(e)
                Dislike.objects.create(comment=form)

            try:
                form.likes
            except Exception as e:
                print(e)
                Like.objects.create(comment=form)
            return redirect("article_detail", article.pk)
    else:
        form = CommentForm()

    context = {
        "article": article,
        "form": form,
        "comments": comments,
        "likes_count": likes_count,
        "dislikes_count": dislikes_count,
        "comments_likes_count": comments_likes_count,
        "comments_dislikes_count": comments_dislikes_count,
    }
    return render(request, "pages/article_detail.html", context)


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
    return render(request, "pages/login.html", context)


def registration_view(request):
    if request.method == "POST":
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegistrationForm()
    context = {
        "form": form
    }
    return render(request, "pages/registration.html", context)


def user_logout(request):
    logout(request)
    return redirect("home")


def add_article(request):
    if request.method == "POST":
        form = ArticleForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.save()
            return redirect("article_detail", form.pk)
    else:
        form = ArticleForm()

    context = {
        "form": form
    }

    return render(request, "pages/article_form.html", context)


def my_articles_view(request, username):
    user = User.objects.filter(username=username).first()
    articles = Article.objects.filter(author=user)
    total_views = sum([article.views for article in articles])
    total_comments = sum([article.comments.all().count() for article in articles])
    days_registered = datetime.now().date() - user.date_joined.date()
    context = {
        "articles": articles,
        "username": username,
        "user": user,
        "total_views": total_views,
        "total_comments": total_comments,
        "days": days_registered.days
    }
    return render(request, "pages/my_articles.html", context)
