"""Test cases related to issues on GitHub."""

import sys
import unittest
from ..mocks import MockOpen

if sys.version_info < (3, 3):
    from mock import patch
else:
    from unittest.mock import patch

if sys.version_info >= (3, 0):
    OPEN = "builtins.open"
else:
    OPEN = "__builtin__.open"


@patch(OPEN, new_callable=MockOpen)
class TestIssues(unittest.TestCase):
    """Test cases related to issues on GitHub."""
    def test_issue_1(self, mock_open):
        """Setting a side effect on a specific open() shouldn't affect
        consecutive calls.
        """
        mock_open["fail_on_open"].side_effect = IOError()

        self.assertRaises(IOError, open, "fail_on_open", "rb")

        with open("success", "r") as handle:
            self.assertEqual("", handle.read())
