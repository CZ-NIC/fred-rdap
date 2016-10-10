"""
Tests of RDAP views.
"""
from django.test import SimpleTestCase


class TestHelpView(SimpleTestCase):
    """
    Test `HelpView` class.
    """
    def test_get(self):
        response = self.client.get('/help')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        self.assertEqual(response['Access-Control-Allow-Origin'], '*')
        data = {
            "rdapConformance": ["rdap_level_0", "fred_version_0"],
            "notices": [{"title": "Help", "description": ["No help."]}],
        }
        self.assertJSONEqual(response.content, data)


class TestUnsupportedView(SimpleTestCase):
    """
    Test `UnsupportedView` class.
    """
    def test_unsupported_view(self):
        response = self.client.get('/autnum/foo')

        self.assertEqual(response.status_code, 501)
        self.assertEqual(response['Content-Type'], 'application/rdap+json')
        self.assertEqual(response.content, '')
