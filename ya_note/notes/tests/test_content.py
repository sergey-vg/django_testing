from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='Note1',
            author=cls.author
        )

    def test_notes_list_for_different_users(self):
        users_statuses = (
            (self.author, True),
            (self.reader, False),
        )
        url = reverse('notes:list')
        for user, status in users_statuses:
            self.client.force_login(user)
            with self.subTest(user=user):
                response = self.client.get(url)
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, status)

    def test_pages_contains_form(self):
        name_args = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in name_args:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                self.client.force_login(self.author)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
