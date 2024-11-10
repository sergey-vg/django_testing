from http import HTTPStatus

from django.test import Client

from .common import BaseTestCase


class TestRoutes(BaseTestCase):

    def test_pages_availability(self):
        """Тест проверяет доступность всех страниц для разных пользователей."""
        parameters = (
            (self.home_url, None, HTTPStatus.OK),
            (self.login_url, None, HTTPStatus.OK),
            (self.logout_url, None, HTTPStatus.OK),
            (self.signup_url, None, HTTPStatus.OK),
            (self.home_url, self.author, HTTPStatus.OK),
            (self.login_url, self.author, HTTPStatus.OK),
            (self.logout_url, self.author, HTTPStatus.OK),
            (self.signup_url, self.author, HTTPStatus.OK),
            (self.note_add_url, self.author, HTTPStatus.OK),
            (self.note_list_url, self.author, HTTPStatus.OK),
            (self.note_success_url, self.author, HTTPStatus.OK),
            (self.note_detail_url, self.author, HTTPStatus.OK),
            (self.note_edit_url, self.author, HTTPStatus.OK),
            (self.note_delete_url, self.author, HTTPStatus.OK),
            (self.note_detail_url, self.reader, HTTPStatus.NOT_FOUND),
            (self.note_edit_url, self.reader, HTTPStatus.NOT_FOUND),
            (self.note_delete_url, self.reader, HTTPStatus.NOT_FOUND),
        )
        for url, user_or_client, status in parameters:
            if user_or_client:
                client = Client()
                client.force_login(user_or_client)
            else:
                client = self.client
            with self.subTest(url=url, client=client):
                response = client.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Тест проверяет, что при попытке перейти на страницу списка заметок,
        страницу успешного добавления записи, страницу добавления заметки,
        отдельной заметки, редактирования или удаления заметки
        анонимный пользователь перенаправляется на страницу логина.э
        """
        urls = (
            self.note_add_url,
            self.note_list_url,
            self.note_success_url,
            self.note_detail_url,
            self.note_edit_url,
            self.note_delete_url,
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
