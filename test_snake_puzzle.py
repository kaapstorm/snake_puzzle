import doctest
from unittest import TestCase

import snake_puzzle


class DocTests(TestCase):

    def test_doctests(self):
        results = doctest.testmod(snake_puzzle)
        self.assertEqual(results.failed, 0)
