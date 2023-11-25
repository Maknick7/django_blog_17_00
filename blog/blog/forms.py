from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Article, Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={
                "class": "form-control"
            })
        }


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "content", "image", "category"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "content": forms.Textarea(attrs={
                "class": "form-control"
            }),
            "image": forms.FileInput(attrs={
                "class": "form-control"
            }),
            "category": forms.Select(attrs={
                "class": "form-select"
            })
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Имя пользователя", widget=forms.TextInput(attrs={
        "class": "form-control"
    }))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={
        "class": "form-control"
    }))

    class Meta:
        model = User


class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={
        "class": "form-control"
    }))
    password2 = forms.CharField(label="Подтвердите Пароль", widget=forms.PasswordInput(attrs={
        "class": "form-control"
    }))

    class Meta:
        model = User
        fields = ["username", "email", "first_name"]
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control"
            }),
            "first_name": forms.TextInput(attrs={
                "class": "form-control"
            }),
        }
