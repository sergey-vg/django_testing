from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from .conftest import HOME_URL, LOGIN_URL, LOGOUT_URL, SIGNUP_URL


@pytest.mark.parametrize(
    'url, client_name, expected_status',
    (
        (HOME_URL, pytest.lazy_fixture('client'), HTTPStatus.OK),
        (HOME_URL, pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('news_detail_url'),
         pytest.lazy_fixture('client'), HTTPStatus.OK),
        (pytest.lazy_fixture('news_detail_url'),
         pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (LOGIN_URL, pytest.lazy_fixture('client'), HTTPStatus.OK),
        (LOGIN_URL, pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (LOGOUT_URL, pytest.lazy_fixture('client'), HTTPStatus.OK),
        (LOGOUT_URL, pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (SIGNUP_URL, pytest.lazy_fixture('client'), HTTPStatus.OK),
        (SIGNUP_URL, pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('comment_edit_url'),
         pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('comment_delete_url'),
         pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('comment_edit_url'), 
         pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('comment_delete_url'),
         pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
    ),
)
def test_pages_availability_for_anonymous_user(
    news, url, client_name, expected_status
):
    response = client_name.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (pytest.lazy_fixture('comment_edit_url'),
        pytest.lazy_fixture('comment_delete_url')),
)
def test_redirect_for_anonymous_client(client, url, comment):
    redirect_url = f'{LOGIN_URL}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
