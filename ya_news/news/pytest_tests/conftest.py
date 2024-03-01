import pytest
from datetime import datetime, timedelta

from django.test.client import Client
from django.conf import settings
from django.urls import reverse

from news.models import News, Comment


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
def comment_id_for_args(comment):
    return (comment.id,)


@pytest.fixture
def comment_form_data(author, news):
    return {
        "news": news,
        "author": author,
        "text": "Текст текст текст",
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
    all_comments = [
        Comment(
            news=news,
            author=author,
            text="Комментарий",
            created=datetime.today() - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    Comment.objects.bulk_create(all_comments)


@pytest.fixture
def detail_url(news_id_for_args):
    return reverse("news:detail", args=news_id_for_args)


@pytest.fixture
def edit_url(comment_id_for_args):
    return reverse("news:edit", args=comment_id_for_args)


@pytest.fixture
def delete_url(comment_id_for_args):
    return reverse("news:delete", args=comment_id_for_args)
