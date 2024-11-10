from http import HTTPStatus

from pytils.translit import slugify

from django.test import Client

from notes.models import Note
from notes.forms import WARNING
from .common import BaseTestCase


class TestLogic(BaseTestCase):
    """Тесты для создания заметок."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)

    def test_user_can_create_note(self):
        """Тест проверяет, что залогиненный пользователь
        может создать заметку.
        """
        notes_count_before = Note.objects.count()
        response = self.auth_author.post(self.note_add_url,
                                         data=self.form_data)
        self.assertRedirects(response, self.note_success_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before + 1)
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    @BaseTestCase.checking_number_notes()
    def test_anonymous_user_cant_create_note(self):
        """Тест проверяет, что анонимный пользователь
        — не может создать заметку.
        """
        response = self.client.post(self.note_add_url, data=self.form_data)
        expected_url = f'{self.login_url}?next={self.note_add_url}'
        self.assertRedirects(response, expected_url)

    def test_empty_slug(self):
        """Тест проверяет, что если при создании заметки не заполнен slug,
        то он формируется автоматически, с помощью функции
        pytils.translit.slugify.
        """
        Note.objects.all().delete()
        self.assertEqual(Note.objects.count(), 0)
        self.form_data.pop('slug')
        response = self.auth_author.post(
            self.note_add_url, data=self.form_data)
        self.assertRedirects(response, self.note_success_url)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    @BaseTestCase.checking_number_notes()
    def test_not_unique_slug(self):
        """Тест проверяет, что невозможно создать две заметки
        с одинаковым slug.
        """
        self.form_data['slug'] = self.note.slug
        response = self.auth_author.post(
            self.note_add_url, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )

    def test_author_can_edit_note(self):
        """Тест проверяет, что пользователь может редактировать
        свои заметки.
        """
        response = self.auth_author.post(self.note_edit_url, self.form_data)
        self.assertRedirects(response, self.note_success_url)
        self.note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    @BaseTestCase.checking_number_notes(expected_change=-1)
    def test_author_can_delete_note(self):
        """Тест проверяет, что пользователь может удалять свои заметки."""
        response = self.auth_author.post(self.note_delete_url)
        self.assertRedirects(response, self.note_success_url)

    @BaseTestCase.checking_number_notes()
    def test_other_user_cant_delete_note(self):
        """Тест проверяет, что пользователь не может удалять чужие заметки."""
        client_auth = Client()
        client_auth.force_login(self.reader)
        response = client_auth.post(self.note_delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_other_user_cant_edit_note(self):
        """Тест проверяет, что пользователь не может редактировать
        чужие заметки.
        """
        comment_before = self.note
        client_auth = Client()
        client_auth.force_login(self.reader)
        response = client_auth.post(self.note_edit_url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        comment_after = Note.objects.get(slug=self.note.slug)
        self.assertEqual(comment_before.title, comment_after.title)
        self.assertEqual(comment_before.text, comment_after.text)
        self.assertEqual(comment_before.slug, comment_after.slug)
        self.assertEqual(comment_before.author, comment_after.author)
