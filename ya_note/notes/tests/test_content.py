from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestNotes(TestCase):
    NOTE_LIST = reverse("notes:list")

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Лев Толстой")
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username="Читатель простой")
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.notes = Note.objects.create(
            title="Заголовок",
            text="Текст",
            slug="zagolovok",
            author=cls.author
        )
        cls.add_url = reverse("notes:add")
        cls.edit_url = reverse("notes:edit", args=(cls.notes.slug,))

    def test_note_in_list_for_author(self):
        url = self.NOTE_LIST
        response = self.author_client.get(url)
        object_list = response.context["object_list"]
        self.assertIn(self.notes, object_list)

    def test_note_not_in_list_for_another_user(self):
        url = self.NOTE_LIST
        response = self.reader_client.get(url)
        object_list = response.context["object_list"]
        self.assertNotIn(self.notes, object_list)

    def test_create_note_page_contains_form(self):
        response = self.author_client.get(self.add_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_note_page_contains_form(self):
        response = self.author_client.get(self.edit_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
