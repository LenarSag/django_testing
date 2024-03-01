# DONE Главная страница доступна анонимному пользователю.
# DONE Страница отдельной новости доступна анонимному пользователю.
# DONE Страницы удаления и редактирования комментария доступны автору комментария.
# DONE При попытке перейти на страницу редактирования или удаления комментария анонимный пользователь перенаправляется на страницу авторизации.
# DONE Авторизованный пользователь не может зайти на страницы редактирования или удаления чужих комментариев (возвращается ошибка 404).
# DONE Страницы регистрации пользователей, входа в учётную запись и выхода из неё доступны анонимным пользователям.
from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    "name, args",
    [
        ("news:home", None),
        ("users:login", None),
        ("users:logout", None),
        ("users:signup", None),
        ("news:detail", pytest.lazy_fixture("news_id_for_args")),
    ],
)
def test_pages_availability_for_anonymous_user(
    client,
    name,
    args,
):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    "parametrized_client, expected_status",
    (
        (pytest.lazy_fixture("not_author_client"), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture("author_client"), HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize(
    "name, args",
    (
        ("news:edit", pytest.lazy_fixture("comment_id_for_args")),
        ("news:delete", pytest.lazy_fixture("comment_id_for_args")),
    ),
)
def test_pages_availability_for_different_users(
    parametrized_client, name, args, expected_status
):
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "name, args",
    (
        ("news:edit", pytest.lazy_fixture("comment_id_for_args")),
        ("news:delete", pytest.lazy_fixture("comment_id_for_args")),
    ),
)
def test_redirects(client, name, args):
    login_url = reverse("users:login")
    url = reverse(name, args=args)
    expected_url = f"{login_url}?next={url}"
    response = client.get(url)
    assertRedirects(response, expected_url)