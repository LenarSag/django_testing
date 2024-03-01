from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TEXT = "Note text"
    NOTE_TITLE = "Title"
    NOTE_SLUG = "Slug"

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Лев Толстой")
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username="Читатель простой")
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.author)
        cls.data_for_db = {
            "title": cls.NOTE_TITLE,
            "text": cls.NOTE_TEXT,
            "slug": cls.NOTE_SLUG,
        }
        cls.add_url = reverse("notes:add")

    def test_unauthorized_cant_create_note(self):
        self.client.post(self.add_url, self.data_for_db)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_authorized_can_create_note(self):
        responce = self.author_client.post(self.add_url, self.data_for_db)
        self.assertRedirects(responce, reverse("notes:success"))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.author)

    def test_empty_slug(self):
        responce = self.author_client.post(
            self.add_url, {"text": "okokok", "title": "no slug here"}
        )
        self.assertRedirects(responce, reverse("notes:success"))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        slug = note.slug
        expected_slug = slugify("no slug here")
        self.assertEqual(expected_slug, slug)


class TestNoteEditDelete(TestCase):
    NOTE_TITLE = "Title"
    NOTE_TEXT = "Note text"
    NEW_NOTE_TEXT = "Note new text"
    NOTE_SLUG = "superslug"

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Лев Толстой")
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username="Читатель простой")
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.author)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE, text=cls.NOTE_TEXT, author=cls.author, slug="someslug"
        )
        cls.data_for_db = {
            "title": cls.NOTE_TITLE,
            "text": cls.NEW_NOTE_TEXT,
            "slug": cls.NOTE_SLUG,
        }
        cls.add_url = reverse("notes:add")
        cls.edit_url = reverse("notes:edit", args=(cls.note.slug,))
        cls.delete_url = reverse("notes:delete", args=(cls.note.slug,))

    def test_only_unique_slag(self):
        self.data_for_db["slug"] = self.note.slug
        response = self.author_client.post(self.add_url, self.data_for_db)
        self.assertFormError(
            response, form="form", field="slug", errors=self.note.slug + WARNING
        )

    def test_authorized_can_edit(self):
        response = self.author_client.post(self.edit_url, self.data_for_db)
        self.assertRedirects(response, reverse("notes:success"))
        self.note.refresh_from_db()
        self.assertEqual(self.NOTE_TITLE, self.note.title)
        self.assertEqual(self.NEW_NOTE_TEXT, self.note.text)
        self.assertEqual(self.NOTE_SLUG, self.note.slug)

    def test_authorized_can_delete(self):
        responce = self.author_client.delete(self.delete_url)
        self.assertRedirects(responce, reverse("notes:success"))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, self.data_for_db)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)
        self.assertEqual(self.note.author, self.author)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
