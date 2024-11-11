from notes.forms import NoteForm
from .common import BaseTestCase


class TestContent(BaseTestCase):

    def test_notes_list_for_different_users(self):
        """Тест проверяет, что отдельная заметка отображается на странице
        со списком заметок в object_list в словаре context и что в список
        заметок одного пользователя не попадают заметки другого пользователя.
        """
        users_statuses = (
            (self.auth_author, True),
            (self.auth_reader, False),
        )
        for user, status in users_statuses:
            with self.subTest(user=user):
                response = user.get(self.note_list_url)
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, status)

    def test_pages_contains_form(self):
        """Тест проверяет, что на страницы создания и редактирования заметки
        передаются формы.
        """
        urls = (
            self.note_add_url,
            self.note_edit_url
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.auth_author.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
