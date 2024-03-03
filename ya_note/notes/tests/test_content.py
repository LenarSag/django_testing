from django.urls import reverse

from notes.forms import NoteForm
from .base_test import CommonTestFunctionality


class TestNotes(CommonTestFunctionality):
    NOTE_LIST = reverse("notes:list")
    ADD_URL = reverse("notes:add")

    def test_note_in_list_for_author(self):
        response = self.author_client.get(self.NOTE_LIST)
        self.assertIn("object_list", response.context)
        object_list = response.context["object_list"]
        self.assertIn(self.notes, object_list)

    def test_note_not_in_list_for_another_user(self):
        response = self.reader_client.get(self.NOTE_LIST)
        self.assertIn("object_list", response.context)
        object_list = response.context["object_list"]
        self.assertNotIn(self.notes, object_list)

    def test_create_note_page_contains_form(self):
        response = self.author_client.get(self.ADD_URL)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], NoteForm)

    def test_edit_note_page_contains_form(self):
        response = self.author_client.get(self.edit_url)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], NoteForm)
