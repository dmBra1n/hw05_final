from django.test import TestCase

from posts.models import Group, Post, User

AMOUNT_SYMBOL: int = 15


class PostModelTest(TestCase):
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
            author=cls.user,
            text='Просто важный текст'
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post_model = PostModelTest.post
        group_model = PostModelTest.group
        expected_post_model_str = post_model.text[:AMOUNT_SYMBOL]
        expected_group_model_str = group_model.title
        self.assertEqual(expected_post_model_str, str(post_model))
        self.assertEqual(expected_group_model_str, str(group_model))
