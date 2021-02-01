from django.test import TestCase, Client
from django.urls import reverse


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.guest_client = Client()

    def test_index_view_correct_template(self):
        """URL-адрес использует шаблон author.html"""
        response = self.guest_client.get(reverse('about:author'))
        self.assertTemplateUsed(response, 'about/author.html')

    def test_group_view_correct_template(self):
        """URL-адрес использует шаблон tech.html"""
        response = self.guest_client.get(reverse('about:tech'))
        self.assertTemplateUsed(response, 'about/tech.html')
