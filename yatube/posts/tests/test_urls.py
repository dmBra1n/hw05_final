from http import HTTPStatus

from django.test import Client, TestCase
from posts.models import Group, Post, User


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Utest')
        cls.group = Group.objects.create(
            title='Просто тайтл',
            slug='some_slug',
            description='Важное описание'
        )
        cls.post = Post.objects.create(
            text='Какой-то текст',
            pub_date='Тест дата',
            author=cls.user,
            group=cls.group,
        )

        cls.templates_url_names = (
            ('/', 'posts/index.html'),
            (f'/group/{cls.group.slug}/', 'posts/group_list.html'),
            (f'/profile/{cls.user.username}/', 'posts/profile.html'),
            (f'/posts/{cls.post.id}/', 'posts/post_detail.html'),
            ('/create/', 'posts/create_post.html'),
            (f'/posts/{cls.post.id}/edit/', 'posts/create_post.html'),
        )
        cls.templates_url_names_public = (
            '/',
            f'/group/{cls.group.slug}/',
            f'/profile/{cls.user.username}/',
            f'/posts/{cls.post.id}/',
        )
        cls.templates_url_names_private = (
            '/create/',
            f'/posts/{cls.post.id}/edit/',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_URLS(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template_name in self.templates_url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_available_URLS_for_guest(self):
        """Страницы доступные неавторизованному пользователю"""
        for url in self.templates_url_names_public:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_not_available_URLS_for_guest(self):
        """Страницы недоступные неавторизованному пользователю"""
        for url in self.templates_url_names_private:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_create_url_redirect_guest(self):
        """Страница /create/ перенаправит неавторизованного клиента
        на страницу авторизации."""
        response = self.guest_client.get('/create/')
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_post_edit_url_redirect_guest(self):
        """Страница posts/post_id/edit/ перенаправит
         неавторизованного клиента на страницу авторизации."""
        response = self.guest_client.get(f'/posts/{self.post.id}/edit/')
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/edit/'
        )

    def test_handler400(self):
        response = self.client.get('/super_test_page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
