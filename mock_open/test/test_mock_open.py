import unittest
from mock import patch, call
from mock_open import MockOpen


@patch("__builtin__.open", new_callable=MockOpen)
class TestOpenSingleFiles(unittest.TestCase):
    """Test the MockOpen and FileLikeMock classes for single file usage."""
    def test_read(self, mock_open):
        """Check effects of reading from an empty file."""
        handle = open("/path/to/file", "r")
        self.assertFalse(handle.closed)
        self.assertEquals("/path/to/file", handle.name)
        self.assertEquals("r", handle.mode)
        self.assertEquals(0, handle.tell())

        text = handle.read()
        self.assertEquals(0, handle.tell())
        self.assertEquals("", text)

        handle.close()
        self.assertTrue(handle.closed)

        self.assertEquals(handle, mock_open.return_value)
        mock_open.assert_called_once_with("/path/to/file", "r")
        handle.read.assert_called_once_with()
        handle.close.assert_called_once_with()

    def test_write(self, mock_open):
        """Check effects of writing to a file."""
        handle = open("/path/to/file", "w")
        self.assertFalse(handle.closed)
        self.assertEquals("/path/to/file", handle.name)
        self.assertEquals("w", handle.mode)
        self.assertEquals(0, handle.tell())

        handle.write("some text\n")
        self.assertEquals(len("some text\n"), handle.tell())
        handle.write("More text!")
        self.assertEquals(
            len("some text\n") + len("More text!"),
            handle.tell())

        handle.close()
        self.assertTrue(handle.closed)

        self.assertEquals(handle, mock_open.return_value)
        mock_open.assert_called_once_with("/path/to/file", "w")
        self.assertEquals(
            [call("some text\n"), call("More text!"), ],
            handle.write.mock_calls)
        handle.close.assert_called_once_with()

    def test_read_as_context_manager(self, mock_open):
        """Check effects of reading from an empty file using a context
        manager.
        """
        with open("/path/to/file", "r") as handle:
            self.assertFalse(handle.closed)
            self.assertEquals("/path/to/file", handle.name)
            self.assertEquals("r", handle.mode)
            self.assertEquals(0, handle.tell())

            text = handle.read()
            self.assertEquals(0, handle.tell())
            self.assertEquals("", text)

        self.assertTrue(handle.closed)
        self.assertEquals(handle, mock_open.return_value)
        mock_open.assert_called_once_with("/path/to/file", "r")
        handle.read.assert_called_once_with()
        handle.close.assert_called_once_with()

    def test_write_as_context_manager(self, mock_open):
        """Check effects of writing to a file using a context manager."""
        with open("/path/to/file", "w") as handle:
            self.assertFalse(handle.closed)
            self.assertEquals("/path/to/file", handle.name)
            self.assertEquals("w", handle.mode)
            self.assertEquals(0, handle.tell())

            handle.write("some text\n")
            self.assertEquals(len("some text\n"), handle.tell())
            handle.write("More text!")
            self.assertEquals(
                len("some text\n") + len("More text!"),
                handle.tell())

        self.assertTrue(handle.closed)
        self.assertEquals(handle, mock_open.return_value)
        mock_open.assert_called_once_with("/path/to/file", "w")
        self.assertEquals(
            [call("some text\n"), call("More text!"), ],
            handle.write.mock_calls)
        handle.close.assert_called_once_with()
