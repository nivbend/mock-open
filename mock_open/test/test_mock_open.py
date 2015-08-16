import unittest
from mock import patch, call, NonCallableMock
from ..mock_open import MockOpen, FileLikeMock
from functools import wraps


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
        self.assertEquals("some text\nMore text!", handle.read_data)
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
        self.assertEquals("some text\nMore text!", handle.read_data)
        handle.close.assert_called_once_with()

    def test_set_contents(self, mock_open):
        """Check setting file's contents before reading from it."""
        contents = [
            "This is the first line",
            "This is the second",
            "This is the third line",
        ]

        # We even allow adding contents to the file incrementally.
        mock_open.return_value.read_data = "\n".join(contents[:-1])
        mock_open.return_value.read_data += "\n" + contents[-1]

        with open("/path/to/file", "r") as handle:
            data = handle.read()

        # Make sure the only call logged was to read().
        handle.write.assert_not_called()
        handle.read.assert_called_once_with()
        self.assertEquals("\n".join(contents), data)

    def test_read_size(self, mock_open):
        """Check reading a certain amount of bytes from the file."""
        mock_open.return_value.read_data = "0123456789"
        with open("/path/to/file", "r") as handle:
            self.assertEquals("0123", handle.read(4))
            self.assertEquals("4567", handle.read(4))
            self.assertEquals("89", handle.read())

    def test_different_read_calls(self, mock_open):
        """Check that read/readline/readlines all work in sync."""
        contents = [
            "Now that she's back in the atmosphere",
            "With drops of Jupiter in her hair, hey, hey, hey",
            "She acts like summer and walks like rain",
            "Reminds me that there's a time to change, hey, hey, hey",
            "Since the return from her stay on the moon",
            "She listens like spring and she talks like June, hey, hey, hey",
        ]

        mock_open.return_value.read_data = "\n".join(contents)
        with open("/path/to/file", "r") as handle:
            first_line = handle.read(len(contents[0]) + 1)
            second_line = handle.readline()
            third_line = handle.read(len(contents[2]) + 1)
            rest = handle.readlines()

            self.assertEquals(contents[0] + "\n", first_line)
            self.assertEquals(contents[1] + "\n", second_line)
            self.assertEquals(contents[2] + "\n", third_line)
            self.assertEquals("\n".join(contents[3:]), "".join(rest))

    def test_different_write_calls(self, mock_open):
        """Check multiple calls to write and writelines."""
        contents = [
            "They paved paradise",
            "And put up a parking lot",
            "With a pink hotel, a boutique",
            "And a swinging hot SPOT",
            "Don't it always seem to go",
            "That you don't know what you've got",
            "'Til it's gone",
            "They paved paradise",
            "And put up a parking lot",
        ]

        with open("/path/to/file", "w") as handle:
            handle.write(contents[0] + "\n")
            handle.write(contents[1] + "\n")
            handle.writelines(line + "\n" for line in contents[2:4])
            handle.write(contents[4] + "\n")
            handle.writelines(line + "\n" for line in contents[5:])

        self.assertEquals(contents, handle.read_data.splitlines())

    def test_iteration(self, mock_open):
        """Test iterating over the file handle."""
        contents = [
            "So bye, bye, Miss American Pie\n",
            "Drove my Chevy to the levee but the levee was dry\n",
            "And them good ole boys were drinking whiskey 'n rye\n",
            "Singin' this'll be the day that I die\n",
            "This'll be the day that I die",
        ]

        mock_open.return_value.read_data = "".join(contents)
        with open("/path/to/file", "r") as handle:
            for (i, line) in enumerate(handle):
                self.assertEquals(contents[i], line)

    def test_getitem_after_call(self, mock_open):
        """Retrieving a handle after the call to open() should give us the same
        object.
        """
        with open("/path/to/file", "r") as handle:
            pass

        self.assertEquals(handle, mock_open["/path/to/file"])

    def test_setting_custom_mock(self, mock_open):
        """Check 'manually' setting a mock for a file."""
        custom_mock = NonCallableMock()
        mock_open["/path/to/file"] = custom_mock

        # Make sure other files aren't affected.
        self.assertIsInstance(open("/path/to/other_file", "r"), FileLikeMock)

        # Check with a regular call.
        self.assertEquals(custom_mock, open("/path/to/file", "r"))

        # Check as a context manager.
        custom_mock.read.side_effect = IOError()
        custom_mock.write.side_effect = IOError()
        with open("/path/to/file") as handle:
            self.assertIs(custom_mock, handle)
            self.assertRaises(IOError, handle.read)
            self.assertRaises(IOError, handle.write, "error")


@patch("__builtin__.open", new_callable=MockOpen)
class TestMultipleCalls(unittest.TestCase):
    """Test multiple calls to open()."""
    def test_read_then_write(self, mock_open):
        """Accessing the same file should handle the same object.

        Reading from a file after writing to it should give us the same
        contents.
        """
        with open("/path/to/file", "w") as first_handle:
            first_handle.write("Ground control to Major Tom")

        with open("/path/to/file", "r") as second_handle:
            contents = second_handle.read()

        self.assertEquals(first_handle, second_handle)
        self.assertEquals("Ground control to Major Tom", contents)

    def test_access_different_files(self, mock_open):
        """Check access to different files with multiple calls to open()."""
        first_handle = mock_open["/path/to/first_file"]
        second_handle = mock_open["/path/to/second_file"]

        first_handle.read_data = "This is the FIRST file"
        second_handle.read_data = "This is the SECOND file"

        with open("/path/to/first_file", "r") as handle:
            self.assertEquals("This is the FIRST file", handle.read())

        with open("/path/to/second_file", "r") as handle:
            self.assertEquals("This is the SECOND file", handle.read())

        # return_value is set to the last handle returned.
        self.assertEquals(second_handle, mock_open.return_value)

        self.assertEquals("/path/to/first_file", first_handle.name)
        self.assertEquals("r", first_handle.mode)
        self.assertEquals("/path/to/second_file", second_handle.name)
        self.assertEquals("r", second_handle.mode)
        first_handle.read.assert_called_once_with()
        second_handle.read.assert_called_once_with()


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

    def test_error_by_name(self, mock_open):
        """Raise an exception for a specific path."""
        mock_open["/path/to/error_file"].side_effect = IOError()

        # Trying to open a different file should be OK.
        with open("/path/to/allowed_file", "r") as allowed_handle:
            pass

        # But openning the bad file should raise an exception.
        self.assertRaises(IOError, open, "/path/to/error_file", "r")

        # Reset open's side effect and check read/write side effects.
        mock_open["/path/to/error_file"].side_effect = None
        mock_open["/path/to/error_file"].read.side_effect = IOError()
        mock_open["/path/to/error_file"].write.side_effect = IOError()
        with open("/path/to/error_file", "r") as handle:
            self.assertRaises(IOError, handle.read)
            self.assertRaises(IOError, handle.write, "Bad write")

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

    def test_wrap_read(self, mock_open):
        """Wrap the normal read() function to add to regular operations.

        This is a method of allowing the mock to behave normally while adding
        our own code around operations.
        """
        def wrap_read(original_read):
            original_side_effect = original_read.side_effect

            @wraps(original_side_effect)
            def wrapped_read(*args, **kws):
                sentinal[0] = True
                return original_side_effect(*args, **kws)

            original_read.side_effect = wrapped_read

        # Avoid uninitialized assignment (see test_hijack_write()).
        sentinal = [False, ]
        mock_open.return_value.read_data = "Some text"
        wrap_read(mock_open.return_value.read)

        with open("/path/to/file", "w") as handle:
            contents = handle.read()

        self.assertEquals("Some text", contents)
        self.assertTrue(sentinal[0])

    def test_wrap_write(self, mock_open):
        """Wrap the normal write() function to add to regular operations.

        This is a method of allowing the mock to behave normally while adding
        our own code around operations.
        """
        def wrap_write(original_write):
            original_side_effect = original_write.side_effect

            @wraps(original_side_effect)
            def wrapped_write(*args, **kws):
                sentinal[0] = True
                return original_side_effect(*args, **kws)

            original_write.side_effect = wrapped_write

        # Avoid uninitialized assignment (see test_hijack_write()).
        sentinal = [False, ]
        wrap_write(mock_open.return_value.write)

        with open("/path/to/file", "w") as handle:
            handle.write("Some text")

        self.assertEquals("Some text", handle.read_data)
        self.assertTrue(sentinal[0])


class TestAPI(unittest.TestCase):
    """Test conformance to mock library's API."""
    def test_read_data(self):
        """Check passing of `read_data` to the constructor."""
        mock_open = MockOpen(read_data="Data from the file")

        with patch("__builtin__.open", mock_open):
            with open("/path/to/file", "r") as handle:
                contents = handle.read()

        self.assertEquals("Data from the file", contents)
