from datetime import datetime, timedelta

import pytest
from functools import wraps
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News
from .constants import COMMENT_TEXT


FORM_DATA = {'text': COMMENT_TEXT}


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news(author):
    news = News.objects.create(title='Заголовок', text='Текст')
    return news


@pytest.fixture
def all_news(author):
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.id, ))


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def comment_edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def comment_delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def all_comments(author, news):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def url_to_comments(news_detail_url):
    return news_detail_url + '#comments'


def checking_number_comments(expected_change=0):
    def decorator(test_func):
        @wraps(test_func)
        def wrapper(*args, **kwargs):
            comments_count_before = Comment.objects.count()
            result = test_func(*args, **kwargs)
            comments_count_after = Comment.objects.count()
            assert comments_count_after == (
                comments_count_before + expected_change)
            return result
        return wrapper
    return decorator


def checking_comment_fields(text=COMMENT_TEXT):
    def decorator(test_func):
        @wraps(test_func)
        def wrapper(*args, **kwargs):
            comment = kwargs.get('comment')
            news = kwargs.get('news')
            author = kwargs.get('author')
            result = test_func(*args, **kwargs)
            comment_after = Comment.objects.get(id=comment.id)
            assert comment_after.text == text
            assert comment_after.news == news
            assert comment_after.author == author
            return result
        return wrapper
    return decorator

"""def checking_comment_fields(test_func):
    @wraps(test_func)
    def wrapper(*args, **kwargs):
        comment = kwargs.get('comment')
        news = kwargs.get('news')
        author = kwargs.get('author')
        comment_after = Comment.objects.get(id=comment.id)
        assert comment_after.text == COMMENT_TEXT
        assert comment_after.news == news
        assert comment_after.author == author
        return test_func(*args, **kwargs)
    return wrapper"""


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')
