from django.test import TestCase

from users.models import User

from ..models import Group, Post


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(username='jacob', password='top_secret1')
        Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        Post.objects.create(
            text='Текст тестового поста',
            author=User.objects.get(pk=1),
            group=Group.objects.get(pk=1)
        )

        cls.post = Post.objects.get(pk=1)
        cls.group = Group.objects.get(pk=1)

    def test_verbose_name(self):
        """verbose_name совпадает с ожидаемым"""
        post = PostModelTest.post
        group = PostModelTest.group

        self.assertEquals(post._meta.get_field('text').verbose_name, 'Текст поста')
        self.assertEquals(group._meta.get_field('title').verbose_name, 'Заголовок')

    def test_help_text(self):
        """help_text совпадает с ожидаемым"""
        post = PostModelTest.post
        group = PostModelTest.group

        self.assertEquals(post._meta.get_field('text').help_text, 'Текст поста должен быть крутым')
        self.assertEquals(group._meta.get_field('title').help_text, 'Придумайте заголовок для группы')

    def test_str_output(self):
        """__str__ совпадает с ожидаемым"""

        post = PostModelTest.post
        group = PostModelTest.group

        self.assertEquals("Сообщество "+self.group.title, str(group))
        self.assertEquals(self.post.text[:15], str(post))
