from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from users.models import User

from ..models import Group, Post, Follow, Comment


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-group',
        )

        cls.another_group = Group.objects.create(
            title='Заголовок',
            slug='second_test-group',
        )

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create(username='username')
        self.user2 = User.objects.create(username='username2')

        self.post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
            group=self.group,
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.authorized_client_two = Client()
        self.authorized_client_two.force_login(self.user2)

    def test_post_in_group(self):
        """ Созданный пост с указанной группой попадает на главную страницу, в страницу группы в которую он добавлен """
        response_main_post = self.guest_client.get('/').context.get('page')[0]
        response_group_post = self.guest_client.get('/group/' + self.group.slug + '/').context.get('page')[0]
        response_another_group_post = self.guest_client.get('/group/' + self.another_group.slug + '/').context.get('page')

        self.assertEqual(response_main_post, self.post)
        self.assertEqual(response_group_post, self.post)
        self.assertEqual(len(response_another_group_post), 0)

    def test_new_post_appearing(self):
        """ Проверка что при post запросе добавляется post и происходит redirect"""
        posts_count = Post.objects.count()

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

        form_data = {
            'text': 'Текст',
            'image': uploaded,
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

    def test_follow_unfollow(self):
        """Проверка появления записи о подписки в бд"""
        follow_count = Follow.objects.count()
        self.authorized_client_two.get('/username/follow/')

        self.assertEqual(Follow.objects.count(), follow_count+1)

        self.authorized_client_two.get('/username/unfollow/')
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_comment(self):
        """ Проверка что при post запросе добавляется comment и происходит redirect"""
        comments_count = Comment.objects.count()

        form_data = {
            'text': 'Текст',
        }
        response = self.authorized_client_two.post(
            reverse('add_comment', kwargs={'username': self.user, 'post_id': self.post.id}),
            data=form_data,
        )

        self.assertRedirects(response, '/'+self.user.username + '/' + str(self.post.id) + '/')
        self.assertEqual(Comment.objects.count(), comments_count + 1)
