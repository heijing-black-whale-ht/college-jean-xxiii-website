import unittest

from app import app


class AppSmokeTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_tailwind_is_enabled_and_bootstrap_css_removed(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('https://cdn.tailwindcss.com', html)
        self.assertNotIn('bootstrap.min.css', html)


if __name__ == '__main__':
    unittest.main()
