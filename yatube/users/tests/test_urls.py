from django.test import TestCase, Client
from posts.models import User


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        user = UsersURLTests.user
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/reset/<uidb64>/<token>/':
                'users/password_reset_confirm.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/password_reset/': 'users/password_reset.html',
            '/auth/password_change/': 'users/password_change.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_unauthorized_users(self):
        """URL-адресы доступны для неавторизованных пользователей."""
        urls_200 = (
            '/auth/signup/',
            '/auth/login/',
            '/auth/reset/done/',
            '/auth/reset/<uidb64>/<token>/',
            '/auth/password_reset/done/',
            '/auth/password_reset/',
            '/auth/logout/',
        )
        urls_302 = (
            '/auth/password_change/',
            '/auth/password_change/done/',
        )
        url_404 = '/auth/unexisting_page/'
        for address in urls_200:
            response = self.guest_client.get(address)
            self.assertEqual(response.status_code, 200)
        for address in urls_302:
            response = self.guest_client.get(address)
            self.assertEqual(response.status_code, 302)
        response = self.guest_client.get(url_404)
        self.assertEqual(response.status_code, 404)

    def test_urls_authorized_users(self):
        """URL-адресы доступны для авторизованных пользователей."""
        urls_200 = (
            '/auth/password_change/',
            '/auth/password_change/done/',
        )
        for address in urls_200:
            response = self.authorized_client.get(address)
            self.assertEqual(response.status_code, 200)
