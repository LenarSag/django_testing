from http import HTTPStatus
import pytest

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


NEW_COMMENT = "Самый новый комментарий"


def test_anonymous_user_cant_create_comment(
        comment_form_data,
        detail_url,
        client
):
    client.post(detail_url, data=comment_form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(comment_form_data, detail_url, author_client):
    response = author_client.post(detail_url, data=comment_form_data)
    assertRedirects(response, f"{detail_url}#comments")
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == comment_form_data["text"]
    assert comment.news == comment_form_data["news"]
    assert comment.author == comment_form_data["author"]


@pytest.mark.django_db
def test_user_cant_use_bad_words(detail_url, author_client):
    bad_words_data = {"text": f"Какой-то текст, {BAD_WORDS[0]}, еще текст"}
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(response, form="form", field="text", errors=WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(delete_url, detail_url, author_client):
    response = author_client.delete(delete_url)
    assertRedirects(response, detail_url + "#comments")
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        delete_url,
        not_author_client
):
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
    edit_url, detail_url, comment, comment_form_data, author_client
):
    comment_form_data["text"] = NEW_COMMENT
    response = author_client.post(edit_url, data=comment_form_data)
    assertRedirects(response, detail_url + "#comments")
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT


def test_user_cant_edit_comment_of_another_user(
    edit_url, comment, comment_form_data, not_author_client
):
    comment_text = comment.text
    response = not_author_client.post(edit_url, data=comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_text
