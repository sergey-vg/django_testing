from functools import wraps

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class BaseTestCase(TestCase):
    """Базовый тестовый класс с общими методами и данными."""
    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='Читатель')
        cls.auth_reader = Client()
        cls.auth_reader.force_login(cls.reader)
        cls.author = User.objects.create(username='Автор')
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='Note1',
            author=cls.author
        )
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        cls.home_url = reverse('notes:home')
        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.signup_url = reverse('users:signup')
        cls.note_list_url = reverse('notes:list')
        cls.note_detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.note_add_url = reverse('notes:add')
        cls.note_edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.note_delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.note_success_url = reverse('notes:success')

    @staticmethod
    def checking_number_notes(expected_change=0):
        def decorator(test_func):
            @wraps(test_func)
            def wrapper(*args, **kwargs):
                notes_count_before = Note.objects.count()
                result = test_func(*args, **kwargs)
                notes_count_after = Note.objects.count()
                assert notes_count_after == (
                    notes_count_before + expected_change)
                return result
            return wrapper
        return decorator
