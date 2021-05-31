import unittest

from models.user.follows import UserFollows

from processing.user.follows import get_user_follows

from constants import TOKEN


class TestTemplate(unittest.TestCase):
    def test_get_contributions(self):
        response = get_user_follows("avgupta456", TOKEN)
        self.assertIsInstance(response, UserFollows)

        # TODO: Add further validation
