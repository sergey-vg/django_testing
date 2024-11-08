from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from .constants import COMMENT_TEXT, NEW_COMMENT_TEXT


def test_anonymous_user_cant_create_comment(
    client, form_data, news_detail_url
):
    client.post(news_detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
    news, author_client, author, form_data, news_detail_url
):
    response = author_client.post(news_detail_url, data=form_data)
    assertRedirects(response, f'{news_detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(not_author_client, news_detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = not_author_client.post(news_detail_url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
    author_client, comment_delete_url, url_to_comments
):
    response = author_client.delete(comment_delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
    not_author_client, comment_delete_url
):
    response = not_author_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
    author_client, comment, url_to_comments, comment_edit_url, form_data
):
    form_data['text'] = NEW_COMMENT_TEXT
    response = author_client.post(comment_edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(
    not_author_client, comment, comment_edit_url, form_data
):
    form_data['text'] = NEW_COMMENT_TEXT
    response = not_author_client.post(comment_edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
