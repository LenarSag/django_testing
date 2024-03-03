from http import HTTPStatus

from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from .base_test import CommonTestFunctionality


ADD_URL = reverse("notes:add")
SUCCESS_URL = reverse("notes:success")


class TestNoteCreation(CommonTestFunctionality):
    LOGIN_URL = reverse("users:login")

    def test_user_can_create_note(self):
        initial_notes_count = self.count_notes()
        responce = self.author_client.post(ADD_URL, self.data_for_db)
        self.assertRedirects(responce, SUCCESS_URL)
        notes_count = self.count_notes()
        self.assertEqual(notes_count, initial_notes_count + 1)

        note = self.get_filtered_note(condition=self.data_for_db['slug'])
        self.assertEqual(note.title, self.data_for_db['title'])
        self.assertEqual(note.text, self.data_for_db['text'])
        self.assertEqual(note.slug, self.data_for_db['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        initial_notes_count = self.count_notes()
        redirect_url = f"{self.LOGIN_URL}?next={ADD_URL}"
        responce = self.client.post(ADD_URL, self.data_for_db)
        notes_count = self.count_notes()
        self.assertEqual(notes_count, initial_notes_count + 0)
        self.assertRedirects(responce, redirect_url)

    def test_empty_slug(self):
        self.data_for_db.pop('slug')
        initial_notes_count = self.count_notes()
        responce = self.author_client.post(
            ADD_URL, data=self.data_for_db
        )
        self.assertRedirects(responce, SUCCESS_URL)
        notes_count = self.count_notes()
        self.assertEqual(notes_count, initial_notes_count + 1)

        expected_slug = slugify(self.data_for_db['title'])
        note = self.get_filtered_note(condition=expected_slug)
        slug = note.slug
        self.assertEqual(expected_slug, slug)

    def test_not_unique_slug(self):
        self.data_for_db["slug"] = self.notes.slug
        response = self.author_client.post(ADD_URL, self.data_for_db)
        self.assertFormError(
            response, form="form",
            field="slug",
            errors=self.notes.slug + WARNING
        )


class TestNoteEditDelete(CommonTestFunctionality):
    def test_author_can_edit_note(self):
        initial_notes_count = self.count_notes()
        note_to_edit = self.get_filtered_note()
        self.assertQuerysetEqual(
            [note_to_edit],
            [repr(self.notes)],
            transform=repr
        )

        response = self.author_client.post(self.edit_url, self.data_for_db)
        self.assertRedirects(response, SUCCESS_URL)
        notes_count = self.count_notes()
        self.assertEqual(notes_count, initial_notes_count)

        self.notes.refresh_from_db()
        self.assertEqual(self.data_for_db['title'], self.notes.title)
        self.assertEqual(self.data_for_db['text'], self.notes.text)
        self.assertEqual(self.data_for_db['slug'], self.notes.slug)

    def test_author_can_delete_note(self):
        initial_notes_count = self.count_notes()
        note_to_delete = self.get_filtered_note()
        self.assertQuerysetEqual(
            [note_to_delete],
            [repr(self.notes)],
            transform=repr
        )

        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, SUCCESS_URL)
        notes_count = self.count_notes()
        self.assertEqual(notes_count, initial_notes_count - 1)

    def test_other_user_cant_edit_note(self):
        initial_notes_count = self.count_notes()
        note_to_edit = self.get_filtered_note()
        self.assertQuerysetEqual(
            [note_to_edit],
            [repr(self.notes)],
            transform=repr
        )

        response = self.reader_client.post(self.edit_url, self.data_for_db)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = self.count_notes()
        self.assertEqual(notes_count, initial_notes_count)

        self.notes.refresh_from_db()
        self.assertEqual(self.notes.text, note_to_edit.text)
        self.assertEqual(self.notes.title, note_to_edit.title)
        self.assertEqual(self.notes.slug, note_to_edit.slug)
        self.assertEqual(self.notes.author, note_to_edit.author)

    def test_user_cant_delete_note_of_another_user(self):
        initial_notes_count = self.count_notes()
        note_to_edit = self.get_filtered_note()
        self.assertQuerysetEqual(
            [note_to_edit],
            [repr(self.notes)],
            transform=repr
        )

        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = self.count_notes()
        self.assertEqual(notes_count, initial_notes_count)
