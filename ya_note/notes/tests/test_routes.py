from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Лев Толстой")
        cls.reader = User.objects.create(username="Читатель простой")
        cls.notes = Note.objects.create(
            title="Заголовок",
            text="Текст",
            slug="zagolovok",
            author=cls.author
        )

    def test_pages_availability_for_anonymous_user(self):
        urls = (
            ("notes:home", None),
            ("users:login", None),
            ("users:logout", None),
            ("users:signup", None),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            names = (
                ("notes:detail", (self.notes.slug,)),
                ("notes:edit", (self.notes.slug,)),
                ("notes:delete", (self.notes.slug,)),
            )
            for name, args in names:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect(self):
        login_url = reverse("users:login")
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
                redirect_url = f"{login_url}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_add_list_success_available(self):
        user = self.author
        self.client.force_login(user)
        names = ("notes:add", "notes:list", "notes:success")
        for name in names:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
