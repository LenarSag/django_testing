from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class CommonTestFunctionality(TestCase):
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
            slug="slug",
            author=cls.author
        )
        cls.data_for_db = {
            "title": 'Заголовок',
            "text": 'Текст',
            "slug": 'new_slug',
        }
        cls.edit_url = reverse("notes:edit", args=(cls.notes.slug,))
        cls.delete_url = reverse("notes:delete", args=(cls.notes.slug,))

    def count_notes(self):
        return Note.objects.count()

    def get_filtered_note(self, condition=None):
        if condition is None:
            condition = self.notes.slug
        return Note.objects.filter(slug=condition).first()
