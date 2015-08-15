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

    def test_set_contents(self, mock_open):
        """Check setting file's contents before reading from it."""
        contents = [
            "This is the first line",
            "This is the second",
            "This is the third line",
        ]

        # We even allow adding contents to the file incrementally.
        mock_open.read_data = "\n".join(contents[:-1])
        mock_open.read_data += "\n" + contents[-1]

        with open("/path/to/file", "r") as handle:
            data = handle.read()

        # Make sure the only call logged was to read().
        handle.write.assert_not_called()
        handle.read.assert_called_once_with()
        self.assertEquals("\n".join(contents), data)


@patch("__builtin__.open", new_callable=MockOpen)
class TestSideEffects(unittest.TestCase):
    """Test setting the side_effect attribute in various situations."""
    def test_error_on_open(self, mock_open):
        """Simulate error openning file."""
        mock_open.side_effect = IOError()

        self.assertRaises(IOError, open, "/not/there", "r")

    def test_error_on_read(self, mock_open):
        """Simulate error when reading from file."""
        mock_open.return_value.read.side_effect = IOError()

        with open("/path/to/file", "w") as handle:
            with self.assertRaises(IOError):
                handle.read()

    def test_error_on_write(self, mock_open):
        """Simulate error when writing to file."""
        mock_open.return_value.write.side_effect = IOError()

        with open("/path/to/file", "r") as handle:
            with self.assertRaises(IOError):
                handle.write("text")

    def test_hijack_read(self, mock_open):
        """Replace the normal read() with a fake one.

        Replacing the side_effect causes the file's inner state to remain
        unchanged after the call to read().
        """
        mock_open.return_value.read.side_effect = lambda: "Hijacked!"

        with open("/path/to/file", "w") as handle:
            contents = handle.read()

        self.assertEquals("Hijacked!", contents)
        self.assertEquals(0, handle.tell())

    def test_hijack_write(self, mock_open):
        """Replace the normal write() with a fake one.

        Replacing the side_effect causes the file's inner state to remain
        unchanged after the call to write().
        """
        def fake_write(data):
            contents[0] = data

        # If we define contents as a 'simple' variable (just None, for example)
        # the assignment inside fake_write() will assign to a local variable
        # instead of the 'outer' contents variable.
        contents = [None, ]
        mock_open.return_value.write.side_effect = fake_write

        with open("/path/to/file", "r") as handle:
            handle.write("text")

        self.assertEquals("text", contents[0])
        self.assertEquals(0, handle.tell())
