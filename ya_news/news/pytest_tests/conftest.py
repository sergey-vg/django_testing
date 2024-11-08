import pytest
from datetime import datetime, timedelta

from django.test.client import Client
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

from news.models import Comment, News
from .constants import COMMENT_TEXT


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
def news_id_for_args(news):
    return (news.id,)


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
    return all_news


@pytest.fixture
def news_detail_url(news_id_for_args):
    return reverse('news:detail', args=news_id_for_args)


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def all_comments(author, news):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return news.comment_set.all()


@pytest.fixture
def comment_id_for_args(comment):
    return (comment.id,)


@pytest.fixture
def url_to_comments(news_detail_url, comment_id_for_args):
    return news_detail_url + '#comments'


@pytest.fixture
def comment_delete_url(comment_id_for_args):
    return reverse('news:delete', args=comment_id_for_args)


@pytest.fixture
def comment_edit_url(comment_id_for_args):
    return reverse('news:edit', args=comment_id_for_args)


@pytest.fixture
def form_data():
    return {'text': COMMENT_TEXT}
