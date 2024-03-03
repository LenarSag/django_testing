from datetime import datetime, timedelta
from random import shuffle

import pytest
from django.test.client import Client
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.models import News, Comment


NUMB_OF_ENG_LETTERS = 26
ORDER_OF_ENG_A = ord('A')


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
def letters_list():
    # создаем список заголовков из англ букв A...Z, AA...AZ..
    letters = [
        chr(ORDER_OF_ENG_A + (index // NUMB_OF_ENG_LETTERS - 1))
        + chr(ORDER_OF_ENG_A + index % NUMB_OF_ENG_LETTERS)
        if index >= NUMB_OF_ENG_LETTERS
        else chr(ORDER_OF_ENG_A + index)
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    shuffle(letters)
    return letters


@pytest.fixture
def date_list():
    dates = [
        timezone.now() - timedelta(days=index)
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    shuffle(dates)
    return dates


@pytest.fixture
def author_list(django_user_model, letters_list):
    users = [
        django_user_model.objects.create(username=name)
        for name in letters_list
    ]
    shuffle(users)
    return users


@pytest.fixture
def news_list(letters_list, date_list):
    # создаем новости с перемешанными датами и заголовками
    all_news = [
        News(
            title=f"{letter}",
            text="Просто текст",
            date=day,
        )
        for letter, day in zip(letters_list, date_list)
    ]

    News.objects.bulk_create(all_news)


@pytest.fixture
def comment_list(news, author_list, letters_list, date_list):
    # создаем комментарии с разными авторами, датами и текстом
    for index in range(11):
        comment = Comment.objects.create(
            news=news, author=author_list[index], text=letters_list[index],
        )
        comment.created = date_list[index]
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
