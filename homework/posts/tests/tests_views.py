from django.test import Client, TestCase
from django.urls import reverse

from users.models import User

from ..models import Group, Post


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-group',
        )

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create(username="username")

        self.post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
            group=self.group,
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_view_correct_template(self):
        """URL-адрес использует шаблон index.html"""
        response = self.authorized_client.get(reverse('index'))
        self.assertTemplateUsed(response, 'index.html')

    def test_group_view_correct_template(self):
        """URL-адрес использует шаблон group.html"""
        response = self.authorized_client.get(reverse('group_posts', kwargs={'slug': 'test-group'}))
        self.assertTemplateUsed(response, 'group.html')

    def test_post_creation_view_correct_template(self):
        """URL-адрес использует шаблон new_post.html"""
        response = self.authorized_client.get(reverse('new_post'))
        self.assertTemplateUsed(response, 'new_post.html')

    def test_post_edit_view_correct_template(self):
        """URL-адрес использует шаблон edit_post.html"""
        response = self.authorized_client.get(reverse('edit_post', kwargs={
            'username': self.user,
            'post_id': self.post.id
        }))
        self.assertTemplateUsed(response, 'post_edit.html')

    def test_follow_view_correct_template(self):
        """URL-адрес использует шаблон follow.html"""
        response = self.authorized_client.get(reverse('follow_index'))
        self.assertTemplateUsed(response, 'follow.html')
