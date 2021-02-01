from django.test import TestCase, Client
from users.models import User
from ..models import Post, Group
from django.urls import reverse
from django import forms


class PostContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Заголовок",
            slug="test-group",
            description="Описание",
        )

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create(username="username")

        self.post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
        )

        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_main_page_context(self):
        """ Шаблон index сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse('index'))
        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author

        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author)

    def test_group_page_context(self):
        """ Шаблон group.html сформирован с правильным контекстом """
        response = self.guest_client.get(reverse('group_posts', kwargs={'slug': "test-group"}))

        group_title = response.context.get('group').title
        group_description = response.context.get('group').description

        self.assertEqual(group_title, self.group.title)
        self.assertEqual(group_description, self.group.description)

    def test_new_post_form_context(self):
        """ Шаблон new_post.html сформирован с правильным контекстом """
        response = self.authorized_user.get(reverse('new_post'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_form_context(self):
        """ Шаблон edit_post.html сформирован с правильным контекстом """
        response = self.authorized_user.get(reverse('edit_post', kwargs={
            'username': 'username',
            'post_id': self.post.id
        }))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_profile_context(self):
        response = self.guest_client.get(reverse('profile', kwargs={'username': 'username'}))

        user_post = response.context.get('page')[0]
        user_username = response.context.get('user_p').username
        user_first_name = response.context.get('user_p').first_name
        user_last_name = response.context.get('user_p').last_name
        user_posts_count = response.context.get('page').paginator.count

        self.assertEqual(user_post, self.post)
        self.assertEqual(user_username, self.user.username)
        self.assertEqual(user_first_name, self.user.first_name)
        self.assertEqual(user_last_name, self.user.last_name)
        self.assertEqual(user_posts_count, 1)

    def test_post_page_context(self):
        response = self.guest_client.get(reverse('post', kwargs={
            'username': self.user.username,
            'post_id': self.post.id
        }))

        post_self = response.context.get('post')
        post_author = response.context.get('author')
        posts_count = response.context.get('posts_count')

        self.assertEqual(post_self, self.post)
        self.assertEqual(post_author, self.user)
        self.assertEqual(posts_count, 1)
