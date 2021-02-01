from django.test import TestCase, Client
from users.models import User
from ..models import Post, Group
from django.urls import reverse


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Заголовок",
            slug="test-group",
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

    # def test_urls_uses_correct_template(self):
    #     """Проверка соответсия шаблонов и URL-адресов"""
    #     templates_url_names = {
    #         'index.html': ['/', ''],
    #         'new_post.html': '/new/',
    #         'group.html': '/group/test-group/',
    #         'profile.html': '/username/',
    #         'post.html': '/username/1/',
    #         'post_edit.html': '/username/1/edit',
    #     }
    #
    #     for template, reverse_name in templates_url_names.items():
    #         with self.subTest():
    #             response = self.authorized_client.get(reverse_name)
    #             self.assertTemplateUsed(response, template)
