import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Utest')

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

        cls.group = Group.objects.create(
            title='Просто тайтл',
            slug='some_slug',
            description='Важное описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Какой-то текст'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.get(username='Utest')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_authorized_client(self):
        """Валидная форма создает новый пост авторизованным пользователем."""
        posts_count = Post.objects.count()
        form_data = {'text': 'Очень важный текст',
                     'image': self.uploaded, }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user.username},
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post_form_authorized_client(self):
        """Валидная форма изменяет пост от авторизованного автора поста"""
        form_data = {'text': 'Изменённый важный текст', }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id},
        ))
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
            ).exists()
        )

    def test_comment_create(self):
        """Проверка создания коментария авторизированным клиентом"""
        comments_count = Comment.objects.count()
        form_data = {'text': 'Важный комментарий'}
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}
        ))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
