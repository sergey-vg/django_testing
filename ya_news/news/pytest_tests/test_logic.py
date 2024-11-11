from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from .constants import COMMENT_TEXT, NEW_COMMENT_TEXT
from .conftest import (FORM_DATA, checking_number_comments,
                       checking_comment_fields)


@checking_number_comments()
def test_anonymous_user_cant_create_comment(client, news_detail_url):
    client.post(news_detail_url, data=FORM_DATA)


def test_user_can_create_comment(
    news, author_client, author, news_detail_url
):
    Comment.objects.all().delete()
    assert Comment.objects.count() == 0
    response = author_client.post(news_detail_url, data=FORM_DATA)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


@checking_number_comments()
def test_user_cant_use_bad_words(not_author_client, news_detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = not_author_client.post(news_detail_url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)


@checking_number_comments(expected_change=-1)
def test_author_can_delete_comment(
    author_client, comment_delete_url, url_to_comments, comment
):
    comment_id = comment.id
    response = author_client.delete(comment_delete_url)
    assertRedirects(response, url_to_comments)
    assert not Comment.objects.filter(id=comment_id).exists()


@checking_comment_fields()
@checking_number_comments()
def test_user_cant_delete_comment_of_another_user(
    comment, news, author, not_author_client, comment_delete_url
):
    response = not_author_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@checking_comment_fields(text=NEW_COMMENT_TEXT)
@checking_number_comments()
def test_author_can_edit_comment(
    author, news, author_client, comment, url_to_comments, comment_edit_url
):
    FORM_DATA['text'] = NEW_COMMENT_TEXT
    response = author_client.post(comment_edit_url, data=FORM_DATA)
    assertRedirects(response, url_to_comments)


@checking_comment_fields()
@checking_number_comments()
def test_user_cant_edit_comment_of_another_user(
    author, news, not_author_client, comment, comment_edit_url
):
    FORM_DATA['text'] = NEW_COMMENT_TEXT
    response = not_author_client.post(comment_edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
