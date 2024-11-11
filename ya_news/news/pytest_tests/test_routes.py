from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'url, client_name, expected_status',
    (
        ('home_url', 'client', HTTPStatus.OK),
        ('home_url', 'author_client', HTTPStatus.OK),
        ('news_detail_url', 'client', HTTPStatus.OK),
        ('news_detail_url', 'author_client', HTTPStatus.OK),
        ('login_url', 'client', HTTPStatus.OK),
        ('login_url', 'author_client', HTTPStatus.OK),
        ('logout_url', 'client', HTTPStatus.OK),
        ('logout_url', 'author_client', HTTPStatus.OK),
        ('signup_url', 'client', HTTPStatus.OK),
        ('signup_url', 'author_client', HTTPStatus.OK),
        ('comment_edit_url', 'author_client', HTTPStatus.OK),
        ('comment_delete_url', 'author_client', HTTPStatus.OK),
        ('comment_edit_url', 'not_author_client', HTTPStatus.NOT_FOUND),
        ('comment_delete_url', 'not_author_client', HTTPStatus.NOT_FOUND),
    )
)
def test_page_access_permissions(
    news, url, client_name, expected_status, request
):
    url = request.getfixturevalue(url)
    client = request.getfixturevalue(client_name)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (pytest.lazy_fixture('comment_edit_url'),
        pytest.lazy_fixture('comment_delete_url')),
)
def test_redirect_for_anonymous_client(client, url, login_url):
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
