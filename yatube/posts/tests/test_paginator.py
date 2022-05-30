from django.test import TestCase, Client
from django.urls import reverse
from ..models import Group, Post, User
from django.conf import settings


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.username = 'auth'
        cls.slug = 'test_slug'
        cls.total_posts = 13
        super().setUpClass()
        cls.user = User.objects.create_user(username=cls.username)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=cls.slug,
            description='Тестовое описание',
        )
        objs = [
            Post(author=cls.user, text=f'Тестовый пост {i}', group=cls.group)
            for i in range(cls.total_posts)
        ]
        Post.objects.bulk_create(objs, cls.total_posts)
        cls.urles = (
            reverse('posts:home'),
            reverse('posts:group_list',
                    kwargs={'slug': PaginatorViewsTest.slug}),
            reverse('posts:profile',
                    kwargs={'username': PaginatorViewsTest.username}),
        )

    def setUp(self):
        # Создаем пользователя
        user = PaginatorViewsTest.user
        # Создаем клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(user)

    def test_first_page_contains_ten_records(self):
        for url in PaginatorViewsTest.urles:
            response = self.client.get(url)
            self.assertEqual(len(response.context['page_obj']),
                             settings.POSTS_PER_PAGE)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        for url in PaginatorViewsTest.urles:
            response = self.client.get(f'{url}?page=2')
            self.assertEqual(
                len(response.context['page_obj']),
                PaginatorViewsTest.total_posts - settings.POSTS_PER_PAGE)
