from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNotes(TestCase):
    NOTE_LIST = reverse("notes:list")

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Лев Толстой")
        cls.reader = User.objects.create(username="Читатель простой")
        cls.notes = Note.objects.create(
            title="Заголовок", text="Текст", slug="zagolovok", author=cls.author
        )
        cls.add_url = reverse("notes:add")

    def test_note_created(self):
        url = self.NOTE_LIST
        user = self.author
        self.client.force_login(user)
        response = self.client.get(url)
        object_list = response.context["object_list"]
        self.assertIn(self.notes, object_list)

    def test_note_not_available_for_other(self):
        url = self.NOTE_LIST
        user = self.reader
        self.client.force_login(user)
        response = self.client.get(url)
        object_list = response.context["object_list"]
        self.assertNotIn(self.notes, object_list)

    # def test_anonymous_client_has_no_form(self):
    #     response = self.client.get(self.add_url)
    #     self.assertNotIn("form", response.context)

    def test_authorized_client_has_form(self):
        user = self.author
        self.client.force_login(user)
        response = self.client.get(self.add_url)
        self.assertIn("form", response.context)
