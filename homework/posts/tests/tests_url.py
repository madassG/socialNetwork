from django.test import TestCase, Client
from users.models import User
from ..models import Post, Group


class StaticURLTests(TestCase):
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

    def test_homepage_access(self):
        """Главная - / - доступна любому пользователю"""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_access(self):
        """Группы - /group/test-group/ - доступна любому пользователю"""
        response = self.guest_client.get('/group/test-group/')
        self.assertEqual(response.status_code, 200)

    def test_new_post_creation_access(self):
        """Создание поста - /new/ - доступна авторизованному пользователю пользователю"""
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_new_post_creation_redirect(self):
        """Редирект со страницы создания поста /new/ для нового пользователя"""
        response = self.guest_client.get('/new/')
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_profile_page_access(self):
        """ Страница профиля пользоателя /<username>/ - доступна любому пользователю"""
        response = self.guest_client.get('/username/')
        self.assertEqual(response.status_code, 200)

    def test_post_page_access(self):
        """ Страница поста, доступная каждому пользователю /<username>/<id>"""
        response = self.guest_client.get('/username/' + str(self.post.id)+'/')
        self.assertEqual(response.status_code, 200)

    def test_post_page_edit_guest_redirect(self):
        """Страница /<username>/<id>/edit доступна только для автора поста"""
        response = self.guest_client.get('/username/' + str(self.post.id) + '/edit')
        self.assertRedirects(response, '/username/' + str(self.post.id) + '/')

    def test_post_edit_not_author_redirect(self):
        user = User.objects.create(username="another")
        post = Post.objects.create(
            text="Текст поста пользователя another",
            author=user,
        )
        response = self.authorized_client.get('/another/' + str(post.id) + '/edit')
        self.assertRedirects(response, '/another/' + str(post.id) + '/')

    def test_post_edit_access(self):
        response = self.authorized_client.get('/username/' + str(self.post.id) + '/edit')
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """Проверка соответсия шаблонов и URL-адресов"""
        templates_url_names = {
            'index.html': '/',
            'new_post.html': '/new/',
            'group.html': '/group/test-group/',
            'profile.html': '/username/',
            'post.html': '/username/1/',
            'post_edit.html': '/username/1/edit',
        }

        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
