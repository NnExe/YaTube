from django.test import TestCase, Client


class AboutURLTests(TestCase):

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()

    def test_urls_available(self):
        """URL-адресы доступны для всех."""
        urls_200 = (
            '/about/author/',
            '/about/tech/',
        )
        url_404 = '/about/unexisting_page/'
        for address in urls_200:
            response = self.guest_client.get(address)
            self.assertEqual(response.status_code, 200)
        response = self.guest_client.get(url_404)
        self.assertEqual(response.status_code, 404)

    def test_urls_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
