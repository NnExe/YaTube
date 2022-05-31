from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import Permission
from ..models import Post, User, Group, Comment


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        permission = Permission.objects.get(name='Может добавлять группы')
        cls.user.user_permissions.add(permission)
        cls.other_user = User.objects.create_user(username='auth1')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

    def setUp(self):
        self.guest_client = Client()
        user = PostFormTests.user
        other_user = PostFormTests.other_user
        self.authorized_client = Client()
        self.authorized_client.force_login(user)
        self.other_authorized_client = Client()
        self.other_authorized_client.force_login(other_user)

    def test_create_post(self):
        """Число постов увеличивается при дополнении."""
        new_text = 'Самый новый пост'
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        data = {
            'text': new_text,
            'image': small_gif,
        }
        old_cout = Post.objects.count()
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=data,
            follow=True
        )
        self.assertLess(old_cout, Post.objects.count())
        self.assertIsNotNone(Post.objects.all()[0].image)

    def test_edit_post(self):
        """Текст поста меняется при редактировании."""
        new_text = 'Самый новый пост'
        post = PostFormTests.post
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}),
            data={'text': new_text},
            follow=True
        )
        self.assertEqual(new_text, Post.objects.get(pk=post.pk).text)

    def test_nonauth_create_post(self):
        """Неавторизованный пользователь не может создать пост."""
        new_text = 'Самый новый пост'
        old_cout = Post.objects.count()
        self.guest_client.post(
            reverse('posts:post_create'),
            data={'text': new_text},
            follow=True
        )
        self.assertEqual(old_cout, Post.objects.count())

    def test_nonauth_edit_post(self):
        """Текст поста не меняется при редактировании анонимом."""
        new_text = 'Самый новый пост'
        post = PostFormTests.post
        old_text = post.text
        self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}),
            data={'text': new_text},
            follow=True
        )
        self.assertEqual(old_text, Post.objects.get(pk=post.pk).text)

    def test_nonauthor_edit_post(self):
        """Текст поста не меняется при редактировании не автором."""
        new_text = 'Самый новый пост'
        post = PostFormTests.post
        old_text = post.text
        self.other_authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}),
            data={'text': new_text},
            follow=True
        )
        self.assertEqual(old_text, Post.objects.get(pk=post.pk).text)

    def test_create_comment(self):
        """Комментарии создаются и видны."""
        data = {
            'text': 'Умный комментарий',
        }
        old_cout = Comment.objects.count()
        responce = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': PostFormTests.post.pk}),
            data=data,
            follow=True
        )
        self.assertLess(old_cout, Comment.objects.count())
        self.assertIn(data['text'], responce.content.decode())

    def test_nonauth_create_comment(self):
        """Неавторизованный пользователь не может создать комментарий."""
        data = {
            'text': 'Глупый комментарий',
        }
        old_cout = Comment.objects.count()
        self.guest_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': PostFormTests.post.pk}),
            data=data,
            follow=True
        )
        self.assertEqual(old_cout, Comment.objects.count())
