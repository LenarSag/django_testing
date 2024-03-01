from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Лев Толстой")
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.data_for_db = {
            "title": 'Заголовок',
            "text": 'Текст',
            "slug": 'slug',
        }
        cls.add_url = reverse("notes:add")

    def test_user_can_create_note(self):
        responce = self.author_client.post(self.add_url, self.data_for_db)
        self.assertRedirects(responce, reverse("notes:success"))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.data_for_db['title'])
        self.assertEqual(note.text, self.data_for_db['text'])
        self.assertEqual(note.slug, self.data_for_db['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.add_url, self.data_for_db)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_empty_slug(self):
        self.data_for_db.pop('slug')
        responce = self.author_client.post(
            self.add_url, data=self.data_for_db
        )
        self.assertRedirects(responce, reverse("notes:success"))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        slug = note.slug
        expected_slug = slugify(self.data_for_db['title'])
        self.assertEqual(expected_slug, slug)


class TestNoteEditDelete(TestCase):
    NOTE_TITLE = "Заголовок"
    NOTE_TEXT = "Текст"
    NEW_NOTE_TEXT = "Новый текст"
    NOTE_SLUG = "slug"

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Лев Толстой")
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username="Читатель простой")
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug=cls.NOTE_SLUG
        )
        cls.data_for_db = {
            "title": cls.NOTE_TITLE,
            "text": cls.NEW_NOTE_TEXT,
            "slug": cls.NOTE_SLUG,
        }
        cls.add_url = reverse("notes:add")
        cls.edit_url = reverse("notes:edit", args=(cls.note.slug,))
        cls.delete_url = reverse("notes:delete", args=(cls.note.slug,))

    def test_not_unique_slug(self):
        self.data_for_db["slug"] = self.note.slug
        response = self.author_client.post(self.add_url, self.data_for_db)
        self.assertFormError(
            response, form="form",
            field="slug",
            errors=self.note.slug + WARNING
        )

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, self.data_for_db)
        self.assertRedirects(response, reverse("notes:success"))
        self.note.refresh_from_db()
        self.assertEqual(self.data_for_db['title'], self.note.title)
        self.assertEqual(self.data_for_db['text'], self.note.text)
        self.assertEqual(self.data_for_db['slug'], self.note.slug)

    def test_author_can_delete_note(self):
        responce = self.author_client.post(self.delete_url)
        self.assertRedirects(responce, reverse("notes:success"))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_other_user_cant_edit_note(self):
        response = self.reader_client.post(self.edit_url, self.data_for_db)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)
        self.assertEqual(self.note.author, self.author)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
