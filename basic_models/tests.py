from django.test import TestCase

from test_project.models import Category


class ActiveModelTestCase(TestCase):
    def test_expected_fields_exist(self):
        category = Category(name='foo')
        self.assertTrue(hasattr(category, 'is_active'))

    def test_expected_defaults(self):
        category = Category(name='bar')
        self.assertTrue(category.is_active)
