from django.test import TestCase, Client
from django.urls import reverse
from ..models import Group, Post, User
from django.conf import settings
from math import ceil


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.username = 'auth'
        cls.slug = 'test_slug'
        cls.add_posts = 3
        # cls.total_posts = 13
        super().setUpClass()
        cls.user = User.objects.create_user(username=cls.username)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=cls.slug,
            description='Тестовое описание',
        )
        objs = [
            Post(author=cls.user, text=f'Тестовый пост {i}', group=cls.group)
            for i in range(cls.add_posts + settings.POSTS_PER_PAGE)
        ]
        Post.objects.bulk_create(objs, cls.add_posts + settings.POSTS_PER_PAGE)
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
        """Проверяем число постов на первой странице."""
        for url in PaginatorViewsTest.urles:
            response = self.client.get(url)
            self.assertEqual(len(response.context['page_obj']),
                             settings.POSTS_PER_PAGE)

    def test_second_page_contains_three_records(self):
        """Проверка: на последней странице должно быть нужное число постов."""
        last_page = 1 + ceil(
            PaginatorViewsTest.add_posts / settings.POSTS_PER_PAGE)
        remainder_posts = (PaginatorViewsTest.add_posts %
                           settings.POSTS_PER_PAGE)
        for url in PaginatorViewsTest.urles:
            response = self.client.get(f'{url}?page={last_page}')
            self.assertEqual(
                len(response.context['page_obj']), remainder_posts)
