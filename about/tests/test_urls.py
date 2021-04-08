from django.test import Client, TestCase


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author_url_exists_at_desired_location(self):
        """Страницы /about/author/ и /about/tech/
         доступны любому пользователю."""
        page_names = ['/about/author/', '/about/tech/']
        for page in page_names:
            with self.subTest():
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, 200)
