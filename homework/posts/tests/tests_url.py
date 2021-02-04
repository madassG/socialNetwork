from django.test import Client, TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from users.models import User

from ..models import Group, Post


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-group',
        )

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create(username='username')
        self.user2 = User.objects.create(username='username2')

        uploaded = SimpleUploadedFile(
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
            image=uploaded,
        )
        self.authorized_client_two = Client()
        self.authorized_client_two.force_login(self.user2)

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
        response = self.authorized_client_two.get('/username/' + str(self.post.id) + '/edit')
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

    def test_post_page_comment_guest_redirect(self):
        """Страница /<username>/<id>/comment доступна только для авторизованного пользователя"""
        response = self.guest_client.get('/username/' + str(self.post.id) + '/comment')
        self.assertRedirects(response, '/auth/login/?next=/' + self.user.username + '/1/comment')

    def test_post_page_comment_get_redirect(self):
        """Страница /<username>/<id>/comment по get запросу выполняет redirect на страницу поста"""
        response = self.authorized_client.get('/username/' + str(self.post.id) + '/comment')
        self.assertRedirects(response, '/username/' + str(self.post.id) + '/')

    def test_follow_unfollow_guest_redirect(self):
        """Страница redirect при попытке неавторизованного пользователя подписаться/отписаться от аккаунта"""
        response_follow = self.guest_client.get('/username/follow/')
        response_unfollow = self.guest_client.get('/username/unfollow/')

        self.assertRedirects(response_follow, '/auth/login/?next=/username/follow/')
        self.assertRedirects(response_unfollow, '/auth/login/?next=/username/unfollow/')

    def test_self_follow_unfollow_authorized_redirect(self):
        """Страница redirect при попытке авторизованного пользователя подписаться/отписаться на/от себя"""
        response_follow = self.authorized_client.get('/username/follow/')
        response_unfollow = self.authorized_client.get('/username/unfollow/')

        self.assertRedirects(response_follow, '/username/')
        self.assertRedirects(response_unfollow, '/username/')

    def test_follow_and_unfollow_success(self):
        """Успешный редирект при подписке/отписке"""
        response_follow = self.authorized_client_two.get('/username/follow/')
        response_unfollow = self.authorized_client_two.get('/username/unfollow/')

        self.assertRedirects(response_follow, '/username/')
        self.assertRedirects(response_unfollow, '/username/')

    def test_urls_uses_correct_template(self):
        """Проверка соответсия шаблонов и URL-адресов"""
        templates_url_names = {
            'index.html': '/',
            'new_post.html': '/new/',
            'group.html': '/group/test-group/',
            'profile.html': '/username/',
            'post.html': '/username/1/',
            'post_edit.html': '/username/1/edit',
            'follow.html': '/follow/'
        }

        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
