import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, User, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Utest')

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.group = Group.objects.create(
            title='Просто группа',
            slug='slug_test',
            description='Важное описание'
        )

        cls.post = Post.objects.create(
            text='Какой-то текст',
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )

        cls.templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}):
                'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': cls.user.username}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.id}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post.id}): 'posts/create_post.html',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.group.title, self.group.title)
        self.assertEqual(first_object.text, self.post.text)

    def test_profile_page_show_correct_context(self):
        """Шаблон профиля сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.user)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertIn('post', response.context)
        self.assertEqual(response.context.get('post').text, self.post.text)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        test_form = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in test_form.items():
            with self.subTest(value=value):
                form = response.context.get('form').fields.get(value)
                self.assertIsInstance(form, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон create_post для редактирования сформирован
                с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        test_form = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in test_form.items():
            with self.subTest(value=value):
                test_form = response.context.get('form').fields.get(value)
                self.assertIsInstance(test_form, expected)

    def test_cache(self):
        """Проверка работы cache"""
        cache_post = Post.objects.create(
            author=self.user,
            text='Важный текст'
        )
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertIn(cache_post, response.context['page_obj'])
        cache_post.delete()
        new_response = self.client.get(reverse('posts:index'))
        self.assertEqual(response.content, new_response.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.FIRST_PAGE = 10
        cls.SECOND_PAGE = 3

        cls.user = User.objects.create_user('Utest')
        cls.group = Group.objects.create(
            title='Просто группа',
            slug='slug_test',
            description='Важное описание',
        )

        cls.posts = Post.objects.bulk_create(
            Post(
                author=cls.user,
                text=f'Просто пост номер: {num}',
                group=cls.group,
            ) for num in range(13)
        )

        cls.templates_pages_names = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse('posts:profile', kwargs={'username': cls.user.username}),
        }

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        """Проверка: количество постов на первой странице равно 10"""
        for reverse_name in self.templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), self.FIRST_PAGE
                )

    def test_second_page_contains_three_records(self):
        """Проверка: на второй странице должно быть три поста"""
        for reverse_name in self.templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']), self.SECOND_PAGE)


class FollowViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Utest')
        cls.follower = User.objects.create(username='Ufollower')
        cls.post = Post.objects.create(
            text='текст',
            author=cls.user
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user)
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)

    def test_follow(self):
        """Проверка подписки на автора"""
        self.follower_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.user})
        )
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        """Проверка отписки от автора"""
        self.follower_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user}))
        self.follower_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.user})
        )
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_post_follow_unfollow(self):
        """Проверка поста в подписках и без подписок"""
        Follow.objects.create(
            user=self.follower,
            author=self.user
        )
        response = self.follower_client.get(
            reverse('posts:follow_index'))
        self.assertIn(self.post, response.context['page_obj'].object_list)
        response = self.author_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(self.post, response.context['page_obj'].object_list)
