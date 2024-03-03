from datetime import datetime, timedelta

import pytest
from django.test.client import Client
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username="Автор")


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username="Не автор")


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title="Заголовок",
        text="Текст заметки",
        date=datetime.today(),
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        text="Текст комментария",
        author=author,
    )
    return comment


@pytest.fixture
def news_id_for_args(news):
    return (news.id,)


@pytest.fixture
def comment_form_data(author, news):
    return {
        "news": news,
        "author": author,
        "text": "Текст текст текст",
    }


@pytest.fixture
def edit_comment_form_data(author, news):
    return {
        "text": "Новый текст",
    }


@pytest.fixture
def news_list():
    all_news = [
        News(
            title=f"Новость {index}",
            text="Просто текст",
            date=datetime.today() - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment_list(news, author):
    now = timezone.now()
    for index in range(11):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def home_url():
    return reverse("news:home")


@pytest.fixture
def login_url():
    return reverse("users:login")


@pytest.fixture
def logout_url():
    return reverse("users:logout")


@pytest.fixture
def signup_url():
    return reverse("users:logout")


@pytest.fixture
def detail_url(news):
    return reverse("news:detail", args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse("news:edit", args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse("news:delete", args=(comment.id,))
