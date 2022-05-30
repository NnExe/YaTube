from django.test import TestCase, Client
from django.urls import reverse
from posts.models import User


class PostFormTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_create_post(self):
        """Пользователь добавляется."""
        data = {
            'first_name': 'user_name',
            'last_name': 'user_surname',
            'username': 'new_user',
            'email': 'new_user@localhost.local',
            'password1': 'P@ssw0rd1',
            'password2': 'P@ssw0rd1'
        }
        old_cout = User.objects.count()
        self.guest_client.post(
            reverse('users:signup'), data=data, follow=True)
        self.assertLess(old_cout, User.objects.count())
