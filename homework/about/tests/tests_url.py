from django.test import Client, TestCase

from users.models import User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.guest_client = Client()

    def test_about_author_and_tech_access(self):
        """Страницы flatpage author по адресу /about/author/ и flatpage tech, доступные каждому"""
        response_author = self.guest_client.get('/about/author/')
        response_tech = self.guest_client.get('/about/tech/')

        self.assertEqual(response_author.status_code, 200)
        self.assertEqual(response_tech.status_code, 200)

    def test_about_author_and_tech_templates(self):
        """Страницы author и tech используют правильные шаблоны"""
        response_author = self.guest_client.get('/about/author/')
        response_tech = self.guest_client.get('/about/tech/')

        self.assertTemplateUsed(response_author, 'about/author.html')
        self.assertTemplateUsed(response_tech, 'about/tech.html')
