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


class TestIssues(unittest.TestCase):
    """Test cases related to issues on GitHub."""
    def test_issue_1(self):
        """Setting a side effect on a specific open() shouldn't affect
        consecutive calls.
        """
        mock_open = MockOpen()
        mock_open["fail_on_open"].side_effect = IOError()

        with patch(OPEN, mock_open):
            with self.assertRaises(IOError):
                open("fail_on_open", "rb")

            with open("success", "r") as handle:
                self.assertEqual("", handle.read())

    def test_issue_3(self):
        """Position in file should be set to 0 after the call to `open`."""
        mock_open = MockOpen(read_data="some content")

        with patch(OPEN, mock_open):
            handle = open("/path/to/file", "r")
            self.assertEqual(0, handle.tell())
            self.assertEqual("some content", handle.read())
