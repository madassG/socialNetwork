from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from users.models import User

from ..models import Group, Post, Comment


class PostContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-group',
            description='Описание',
        )

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create(username='username')
        self.user2 = User.objects.create(username='username2')

        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=(b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B'),
            content_type='image/gif',

        )
        self.post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
            group=self.group,
            image=self.uploaded,
        )

        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

        self.authorized_user_two = Client()
        self.authorized_user_two.force_login(self.user2)

    def test_main_page_context(self):
        """ Шаблон index сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse('index'))
        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author

        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author)

    def test_group_page_context(self):
        """ Шаблон group.html сформирован с правильным контекстом """
        response = self.guest_client.get(reverse('group_posts', kwargs={'slug': 'test-group'}))

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
            'image': forms.fields.FileField,
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
            'image': forms.fields.FileField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_profile_context(self):
        """Тест профиля"""
        response = self.guest_client.get(reverse('profile', kwargs={'username': 'username'}))

        user_post = response.context.get('page')[0]
        user_username = response.context.get('user_p').username
        user_first_name = response.context.get('user_p').first_name
        user_last_name = response.context.get('user_p').last_name
        user_posts_count = response.context.get('page').paginator.count

        self.assertEqual(user_post.image, self.post.image)
        self.assertEqual(user_post, self.post)
        self.assertEqual(user_username, self.user.username)
        self.assertEqual(user_first_name, self.user.first_name)
        self.assertEqual(user_last_name, self.user.last_name)
        self.assertEqual(user_posts_count, 1)

    def test_comments_under_post_context(self):
        """Проверка, что комментарии передаются в контекст с постом"""
        comment = Comment.objects.create(
            text='Текст комментария',
            post=self.post,
            author=self.user2,
        )

        response = self.authorized_user.get(reverse('post', kwargs={
            'username': self.user.username, 'post_id': self.post.id
        }))

        comments = response.context.get('comments')
        self.assertIsNotNone(comments)

    def test_post_page_context(self):
        """Проверка страницы с постом"""
        response = self.guest_client.get(reverse('post', kwargs={
            'username': self.user.username,
            'post_id': self.post.id
        }))

        post_self = response.context.get('post')
        post_author = response.context.get('author')
        posts_count = response.context.get('author').user_posts.count()

        self.assertEqual(post_self.image, self.post.image)
        self.assertEqual(post_self, self.post)
        self.assertEqual(post_author, self.user)
        self.assertEqual(posts_count, 1)

    def test_post_appearing_in_follow_page_after_following_context(self):
        self.authorized_user_two.get('/username/follow/')
        response_follow = self.authorized_user_two.get('/follow/')
        post = response_follow.context.get('page')[0]

        self.authorized_user_two.get('/username/unfollow/')
        response_unfollow = self.authorized_user_two.get('/follow/')
        no_post = response_unfollow.context.get('page')

        self.assertEqual(post, self.post)
        self.assertEqual(len(no_post), 0)
