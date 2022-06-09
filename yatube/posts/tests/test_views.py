import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Page
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')
        cls.user = User.objects.create_user(username='auth')
        cls.other_user = User.objects.create_user(username='other_auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            image=cls.image,
            group=cls.group
        )
        cls.urls = (
            ('posts:home', None, 'posts/index.html'),
            ('posts:group_list', (cls.group.slug,), 'posts/group_list.html'),
            ('posts:profile', (cls.post.author.username,),
             'posts/profile.html'),
            ('posts:post_detail', (cls.post.pk,), 'posts/post_detail.html'),
            ('posts:post_edit', (cls.post.pk,), 'posts/create_post.html'),
            ('posts:post_create', None, 'posts/create_post.html'),
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        user = PostsViewsTests.user
        other_user = PostsViewsTests.other_user
        self.authorized_client = Client()
        self.authorized_client.force_login(user)
        self.other_authorized_client = Client()
        self.other_authorized_client.force_login(other_user)

    def test_aview_in_context(self):
        urls = (
            ('posts:home', None, 'posts/index.html'),
            ('posts:group_list', (PostsViewsTests.group.slug,),
             'posts/group_list.html'),
            ('posts:profile', (PostsViewsTests.post.author.username,),
             'posts/profile.html'),
        )
        for reverse_name, args, template in urls:
            address = reverse(reverse_name, args=args)
            cache.clear()
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                post = response.context['page_obj'][0]
                self.assertEqual(PostsViewsTests.post.image, post.image)
        post_url = reverse('posts:post_detail',
                           args=(PostsViewsTests.post.pk,))
        response = self.authorized_client.get(post_url)
        post = response.context['post']
        self.assertEqual(PostsViewsTests.post.image, post.image)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        for reverse_name, args, template in PostsViewsTests.urls:
            address = reverse(reverse_name, args=args)
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:home'))
        self.assertIn('page_obj', response.context)
        self.assertContains(response, '<img', html=False)
        self.assertIsInstance(response.context['page_obj'], Page)

    def test_groups_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        group = PostsViewsTests.group
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': group.slug}))
        posts = response.context['page_obj']
        self.assertIn('page_obj', response.context)
        self.assertIsInstance(posts, Page)
        for post in posts:
            self.assertEqual(post.group.slug, group.slug)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        post = PostsViewsTests.post
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': post.author.username}))
        posts = response.context['page_obj']
        self.assertIn('page_obj', response.context)
        self.assertIsInstance(posts, Page)
        for post in posts:
            self.assertEqual(post.author, PostsViewsTests.user)

    def test_profile_post_detail_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        post = PostsViewsTests.post
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': post.pk}))
        self.assertIn('post', response.context)
        self.assertIsInstance(response.context['post'], Post)
        self.assertEqual(response.context['post'].pk, post.pk)

    def test_profile_post_edit_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        post = PostsViewsTests.post
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': post.pk}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        self.assertIn('form', response.context)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_profile_post_create_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        self.assertIn('form', response.context)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_view_on_pages(self):
        """Добавленный пост отображаетя на нужных страницах."""
        group = PostsViewsTests.group
        post_with_group = Post.objects.create(
            author=PostsViewsTests.user,
            text='Тестовый пост',
            group=PostsViewsTests.group,
        )
        another_group = Group.objects.create(
            title='Еще одна тестовая группа',
            slug='other_test_slug',
            description='Еще одно тестовое описание',
        )
        urls = {
            reverse('posts:home'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': group.slug}
                    ): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': post_with_group.author.username}):
                    'posts/profile.html',
        }
        for url in urls:
            response = self.client.get(url)
            self.assertIn(post_with_group.text, response.content.decode())
        response = self.client.get(reverse(
            'posts:group_list', kwargs={'slug': another_group.slug}),)
        self.assertNotIn(post_with_group.text, response.content.decode())

    def test_cache(self):
        """Тестируем кэш."""
        cache.clear()
        temp_post = Post.objects.create(
            author=PostsViewsTests.user,
            text='Тестовый пост'
        )
        response = self.authorized_client.get(reverse('posts:home'))
        post_save = response.content
        temp_post.delete()
        response = self.authorized_client.get(reverse('posts:home'))
        self.assertEqual(post_save, response.content)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:home'))
        self.assertNotEqual(post_save, response.content)

    def test_follow_user(self):
        """Тестируем подписки."""
        followers = Follow.objects.count()
        self.client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': PostsViewsTests.user.username}))
        self.assertEqual(
            followers,
            Follow.objects.count()
        )
        self.other_authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': PostsViewsTests.user.username}))
        self.assertNotEqual(
            followers,
            Follow.objects.count()
        )

    def test_follow_view(self):
        """Тестируем отображение постов подписки."""
        third_user = User.objects.create_user(username='third_auth')
        self.third_client = Client()
        self.third_client.force_login(third_user)
        # Подписываем второго
        self.other_authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': PostsViewsTests.user.username}))
        response = self.other_authorized_client.get(
            reverse('posts:follow_index'))
        self.assertIn(PostsViewsTests.post.text,
                      response.content.decode())
        response = self.third_client.get(
            reverse('posts:follow_index'))
        self.assertNotIn(PostsViewsTests.post.text, response.content.decode())
