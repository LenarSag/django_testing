from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    "url_fixture",
    (
        "home_url",
        "login_url",
        "logout_url",
        "signup_url",
        "detail_url",
    )
)
def test_pages_availability_for_anonymous_user(
    client,
    request,
    url_fixture,
):
    url = request.getfixturevalue(url_fixture)
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
    "url_fixture",
    (
        "edit_url",
        "delete_url",
    )
)
def test_pages_availability_for_different_users(
    request, parametrized_client, url_fixture, expected_status
):
    url = request.getfixturevalue(url_fixture)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "url_fixture",
    (
        "edit_url",
        "delete_url",
    )
)
def test_redirects(client, request, url_fixture, login_url):
    redirect_login_url = login_url
    url = request.getfixturevalue(url_fixture)
    expected_url = f"{redirect_login_url}?next={url}"
    response = client.get(url)
    assertRedirects(response, expected_url)
