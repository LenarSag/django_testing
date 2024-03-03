from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from .base_test import CommonTestFunctionality


User = get_user_model()


class TestRoutes(CommonTestFunctionality):
    URLS = (
        ("notes:home"),
        ("users:login"),
        ("users:logout"),
        ("users:signup"),
    )
    LOGIN_URL = reverse("users:login")

    def test_pages_availability_for_anonymous_user(self):
        for name in self.URLS:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for user_client, status in users_statuses:
            names = (
                ("notes:detail", (self.notes.slug,)),
                ("notes:edit", (self.notes.slug,)),
                ("notes:delete", (self.notes.slug,)),
            )
            for name, args in names:
                with self.subTest(user=user_client, name=name):
                    url = reverse(name, args=args)
                    response = user_client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect(self):
        names = (
            ("notes:add", None),
            ("notes:list", None),
            ("notes:success", None),
            ("notes:detail", (self.notes.slug,)),
            ("notes:edit", (self.notes.slug,)),
            ("notes:delete", (self.notes.slug,)),
        )
        for name, args in names:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f"{self.LOGIN_URL}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_add_list_success_available(self):
        names = ("notes:add", "notes:list", "notes:success")
        for name in names:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
