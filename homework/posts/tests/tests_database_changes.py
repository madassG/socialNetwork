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

        cls.another_group = Group.objects.create(
            title="Заголовок",
            slug="second_test-group",
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

    def test_post_in_group(self):
        """ Созданный пост с указанной группой попадает на главную страницу, в страницу группы в которую он добавлен """
        response_main_post = self.guest_client.get('/').context.get('page')[0]
        response_group_post = self.guest_client.get('/group/' + self.group.slug + '/').context.get('page')[0]
        response_another_group_post = self.guest_client.get('/group' + self.another_group.slug + '/').context.get('page')

        self.assertEqual(response_main_post, self.post)
        self.assertEqual(response_group_post, self.post)
        self.assertIsNone(response_another_group_post)

    def test_new_post_appearing(self):
        """ Проверка что при post запросе добавляется post и происходит redirect"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст',
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
        )

        self.assertRedirects(response, '/')
        self.assertEqual(Post.objects.count(), posts_count+1)

    def test_edit_post(self):
        """ Проверка что при post запросе изменяется post и происходит redirect"""
        post_id = self.post.id
        form_data = {
            'text': 'Текст',
        }
        response = self.authorized_client.post(
            reverse('edit_post', kwargs={'username': self.user.username, 'post_id': self.post.id}),
            data=form_data,
        )

        self.assertRedirects(response, '/username/' + str(self.post.id) + '/')
        self.assertEqual(Post.objects.get(id=post_id).text, form_data['text'])
