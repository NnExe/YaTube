from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        user = PostsURLTests.user
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        post = PostsURLTests.post
        group = PostsURLTests.group
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{group.slug}/': 'posts/group_list.html',
            f'/profile/{post.author.username}/': 'posts/profile.html',
            f'/posts/{post.pk}/': 'posts/post_detail.html',
            f'/posts/{post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        cache.clear()
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_unauthorized_users(self):
        """URL-адресы доступны для неавторизованных пользователей."""
        post = PostsURLTests.post
        group = PostsURLTests.group
        urls_200 = (
            '/',
            f'/profile/{post.author.username}/',
            f'/posts/{post.pk}/',
            f'/group/{group.slug}/',
        )
        urls_302 = (
            '/create/',
            f'/posts/{post.pk}/edit/'
        )
        url_404 = '/unexisting_page/'
        for address in urls_200:
            response = self.guest_client.get(address)
            self.assertEqual(response.status_code, 200)
        for address in urls_302:
            response = self.guest_client.get(address)
            self.assertEqual(response.status_code, 302)
        response = self.guest_client.get(url_404)
        self.assertEqual(response.status_code, 404)

    def test_urls_author_users(self):
        """URL-адресы доступные только для автора."""
        post = PostsURLTests.post
        nonauthor = User.objects.create_user(username='clone')
        clone_client = Client()
        clone_client.force_login(nonauthor)
        urls = (
            f'/posts/{post.pk}/edit/',
        )
        for address in urls:
            response = self.guest_client.get(address)
            self.assertEqual(response.status_code, 302)
            response = clone_client.get(address)
            self.assertEqual(response.status_code, 302)
            response = self.authorized_client.get(address)
            self.assertEqual(response.status_code, 200)

    def test_urls_authorized_users(self):
        """URL-адресы доступные только для авторизованных пользователей."""
        urls = (
            '/create/',
        )
        for address in urls:
            response = self.guest_client.get(address)
            self.assertEqual(response.status_code, 302)
            response = self.authorized_client.get(address)
            self.assertEqual(response.status_code, 200)
