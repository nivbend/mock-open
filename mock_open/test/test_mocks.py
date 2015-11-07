"""Test cases for the mocks module."""

import sys
import unittest
from functools import wraps
from ..mocks import MockOpen, FileLikeMock

if sys.version_info < (3, 3):
    from mock import patch, call, NonCallableMock, DEFAULT
else:
    from unittest.mock import patch, call, NonCallableMock, DEFAULT

if sys.version_info >= (3, 0):
    OPEN = 'builtins.open'
else:
    OPEN = '__builtin__.open'


@patch(OPEN, new_callable=MockOpen)
class TestOpenSingleFiles(unittest.TestCase):
    """Test the MockOpen and FileLikeMock classes for single file usage."""
    def test_read(self, mock_open):
        """Check effects of reading from an empty file."""
        handle = open('/path/to/file', 'r')
        self.assertFalse(handle.closed)
        self.assertEqual('/path/to/file', handle.name)
        self.assertEqual('r', handle.mode)
        self.assertEqual(0, handle.tell())

        text = handle.read()
        self.assertEqual(0, handle.tell())
        self.assertEqual('', text)

        handle.close()
        self.assertTrue(handle.closed)

        self.assertEqual(handle, mock_open.return_value)
        mock_open.assert_called_once_with('/path/to/file', 'r')
        handle.read.assert_called_once_with()
        handle.close.assert_called_once_with()

    def test_write(self, mock_open):
        """Check effects of writing to a file."""
        handle = open('/path/to/file', 'w')
        self.assertFalse(handle.closed)
        self.assertEqual('/path/to/file', handle.name)
        self.assertEqual('w', handle.mode)
        self.assertEqual(0, handle.tell())

        handle.write("some text\n")
        self.assertEqual(len("some text\n"), handle.tell())
        handle.write('More text!')
        self.assertEqual(
            len('some text\n') + len('More text!'),
            handle.tell())

        handle.close()
        self.assertTrue(handle.closed)

        self.assertEqual(handle, mock_open.return_value)
        mock_open.assert_called_once_with('/path/to/file', 'w')
        self.assertEqual(
            [call('some text\n'), call('More text!'), ],
            handle.write.mock_calls)
        self.assertEqual('some text\nMore text!', handle.read_data)
        handle.close.assert_called_once_with()

    def test_read_as_context_manager(self, mock_open):
        """Check effects of reading from an empty file using a context
        manager.
        """
        with open('/path/to/file', 'r') as handle:
            self.assertFalse(handle.closed)
            self.assertEqual('/path/to/file', handle.name)
            self.assertEqual('r', handle.mode)
            self.assertEqual(0, handle.tell())

            text = handle.read()
            self.assertEqual(0, handle.tell())
            self.assertEqual('', text)

        self.assertTrue(handle.closed)
        self.assertEqual(handle, mock_open.return_value)
        mock_open.assert_called_once_with('/path/to/file', 'r')
        handle.read.assert_called_once_with()
        handle.close.assert_called_once_with()

    def test_write_as_context_manager(self, mock_open):
        """Check effects of writing to a file using a context manager."""
        with open('/path/to/file', 'w') as handle:
            self.assertFalse(handle.closed)
            self.assertEqual('/path/to/file', handle.name)
            self.assertEqual('w', handle.mode)
            self.assertEqual(0, handle.tell())

            handle.write("some text\n")
            self.assertEqual(len("some text\n"), handle.tell())
            handle.write('More text!')
            self.assertEqual(
                len('some text\n') + len('More text!'),
                handle.tell())

        self.assertTrue(handle.closed)
        self.assertEqual(handle, mock_open.return_value)
        mock_open.assert_called_once_with('/path/to/file', 'w')
        self.assertEqual(
            [call('some text\n'), call('More text!'), ],
            handle.write.mock_calls)
        self.assertEqual('some text\nMore text!', handle.read_data)
        handle.close.assert_called_once_with()

    def test_seek(self, _):
        """Check calling seek()."""
        with open('/path/to/file', 'w+') as handle:
            handle.write('There\'s no place like home')
            handle.seek(len('There\'s '))
            self.assertEqual('no place like home', handle.read())

    def test_set_contents(self, mock_open):
        """Check setting file's contents before reading from it."""
        contents = [
            'This is the first line',
            'This is the second',
            'This is the third line',
        ]

        # We even allow adding contents to the file incrementally.
        mock_open.return_value.read_data = '\n'.join(contents[:-1])
        mock_open.return_value.read_data += '\n' + contents[-1]

        with open('/path/to/file', 'r') as handle:
            data = handle.read()

        # Make sure the only call logged was to read().
        handle.write.assert_not_called()
        handle.read.assert_called_once_with()
        self.assertEqual('\n'.join(contents), data)

    def test_read_size(self, mock_open):
        """Check reading a certain amount of bytes from the file."""
        mock_open.return_value.read_data = '0123456789'
        with open('/path/to/file', 'r') as handle:
            self.assertEqual('0123', handle.read(4))
            self.assertEqual('4567', handle.read(4))
            self.assertEqual('89', handle.read())

    def test_different_read_calls(self, mock_open):
        """Check that read/readline/readlines all work in sync."""
        contents = [
            'Now that she\'s back in the atmosphere',
            'With drops of Jupiter in her hair, hey, hey, hey',
            'She acts like summer and walks like rain',
            'Reminds me that there\'s a time to change, hey, hey, hey',
            'Since the return from her stay on the moon',
            'She listens like spring and she talks like June, hey, hey, hey',
        ]

        mock_open.return_value.read_data = '\n'.join(contents)
        with open('/path/to/file', 'r') as handle:
            first_line = handle.read(len(contents[0]) + 1)
            second_line = handle.readline()
            third_line = handle.read(len(contents[2]) + 1)
            rest = handle.readlines()

            self.assertEqual(contents[0] + '\n', first_line)
            self.assertEqual(contents[1] + '\n', second_line)
            self.assertEqual(contents[2] + '\n', third_line)
            self.assertEqual('\n'.join(contents[3:]), ''.join(rest))

    def test_different_write_calls(self, _):
        """Check multiple calls to write and writelines."""
        contents = [
            'They paved paradise',
            'And put up a parking lot',
            'With a pink hotel, a boutique',
            'And a swinging hot SPOT',
            'Don\'t it always seem to go',
            'That you don\'t know what you\'ve got',
            '\'Til it\'s gone',
            'They paved paradise',
            'And put up a parking lot',
        ]

        with open('/path/to/file', 'w') as handle:
            handle.write(contents[0] + '\n')
            handle.write(contents[1] + '\n')
            handle.writelines(line + '\n' for line in contents[2:4])
            handle.write(contents[4] + '\n')
            handle.writelines(line + '\n' for line in contents[5:])

        self.assertEqual(contents, handle.read_data.splitlines())

    def test_iteration(self, mock_open):
        """Test iterating over the file handle."""
        contents = [
            "So bye, bye, Miss American Pie\n",
            "Drove my Chevy to the levee but the levee was dry\n",
            "And them good ole boys were drinking whiskey 'n rye\n",
            "Singin' this'll be the day that I die\n",
            'This\'ll be the day that I die',
        ]

        mock_open.return_value.read_data = ''.join(contents)
        with open('/path/to/file', 'r') as handle:
            for (i, line) in enumerate(handle):
                self.assertEqual(contents[i], line)

    def test_getitem_after_call(self, mock_open):
        """Retrieving a handle after the call to open() should give us the same
        object.
        """
        with open('/path/to/file', 'r') as handle:
            pass

        self.assertEqual(handle, mock_open['/path/to/file'])

    def test_setting_custom_mock(self, mock_open):
        """Check 'manually' setting a mock for a file."""
        custom_mock = NonCallableMock()
        mock_open['/path/to/file'] = custom_mock

        # Make sure other files aren't affected.
        self.assertIsInstance(open('/path/to/other_file', 'r'), FileLikeMock)

        # Check with a regular call.
        self.assertEqual(custom_mock, open('/path/to/file', 'r'))

        # Check as a context manager.
        custom_mock.read.side_effect = IOError()
        custom_mock.write.side_effect = IOError()
        with open('/path/to/file') as handle:
            self.assertIs(custom_mock, handle)
            self.assertRaises(IOError, handle.read)
            self.assertRaises(IOError, handle.write, 'error')


@patch(OPEN, new_callable=MockOpen)
class TestMultipleCalls(unittest.TestCase):
    """Test multiple calls to open()."""
    def test_read_then_write(self, _):
        """Accessing the same file should handle the same object.

        Reading from a file after writing to it should give us the same
        contents.
        """
        with open('/path/to/file', 'w') as first_handle:
            first_handle.write('Ground control to Major Tom')

        with open('/path/to/file', 'r') as second_handle:
            contents = second_handle.read()

        self.assertEqual(first_handle, second_handle)
        self.assertEqual('Ground control to Major Tom', contents)

    def test_access_different_files(self, mock_open):
        """Check access to different files with multiple calls to open()."""
        first_handle = mock_open['/path/to/first_file']
        second_handle = mock_open['/path/to/second_file']

        # Paths should be set when created, if possible.
        # Note this isn't the case when not specifically instantiating a file
        # mock (eg., by using `return_value` instead).
        self.assertEqual('/path/to/first_file', first_handle.name)
        self.assertEqual('/path/to/second_file', second_handle.name)

        first_handle.read_data = 'This is the FIRST file'
        second_handle.read_data = 'This is the SECOND file'

        with open('/path/to/first_file', 'r') as handle:
            self.assertEqual('/path/to/first_file', handle.name)
            self.assertEqual('This is the FIRST file', handle.read())

        with open('/path/to/second_file', 'r') as handle:
            self.assertEqual('/path/to/second_file', handle.name)
            self.assertEqual('This is the SECOND file', handle.read())

        # return_value is set to the last handle returned.
        self.assertEqual(second_handle, mock_open.return_value)

        self.assertEqual('r', first_handle.mode)
        self.assertEqual('r', second_handle.mode)
        first_handle.read.assert_called_once_with()
        second_handle.read.assert_called_once_with()

    def test_return_value(self, mock_open):
        """Check that `return_value` always returns the last file mock."""
        with open('/path/to/first_file', 'r'):
            pass

        with open('/path/to/second_file', 'r') as handle:
            self.assertEqual(handle, mock_open.return_value)


@patch(OPEN, new_callable=MockOpen)
class TestSideEffects(unittest.TestCase):
    """Test setting the side_effect attribute in various situations."""
    def test_error_on_open(self, mock_open):
        """Simulate error openning a file."""
        mock_open.side_effect = IOError()

        self.assertRaises(IOError, open, '/not/there', 'r')

    def test_error_on_any_open(self, mock_open):
        """Simulate errors opening any file."""
        mock_open.side_effect = IOError()

        self.assertRaises(IOError, open, '/not/there_1', 'r')
        self.assertRaises(IOError, open, '/not/there_2', 'r')
        self.assertRaises(IOError, open, '/not/there_3', 'r')

    def test_error_on_all_but_one(self, mock_open):
        """Setting a global error but allowing specific file/s."""
        mock_open.side_effect = IOError()
        mock_open['/is/there'].side_effect = None

        self.assertRaises(IOError, open, '/not/there_1', 'r')
        self.assertRaises(IOError, open, '/not/there_2', 'r')

        with open('/is/there', 'r'):
            pass

    def test_error_list(self, mock_open):
        """Setting a global side effect iterator."""
        mock_open.side_effect = [ValueError(), RuntimeError(), DEFAULT, ]

        self.assertRaises(ValueError, open, '/not/there_1', 'r')
        self.assertRaises(RuntimeError, open, '/not/there_2', 'r')

        with open('/is/there', 'r'):
            pass

    def test_error_on_read(self, mock_open):
        """Simulate error when reading from file."""
        mock_open.return_value.read.side_effect = IOError()

        with open('/path/to/file', 'w') as handle:
            with self.assertRaises(IOError):
                handle.read()

    def test_error_on_write(self, mock_open):
        """Simulate error when writing to file."""
        mock_open.return_value.write.side_effect = IOError()

        with open('/path/to/file', 'r') as handle:
            with self.assertRaises(IOError):
                handle.write('text')

    def test_error_by_name(self, mock_open):
        """Raise an exception for a specific path."""
        mock_open['/path/to/error_file'].side_effect = IOError()

        # Trying to open a different file should be OK.
        with open('/path/to/allowed_file', 'r'):
            pass

        # But openning the bad file should raise an exception.
        self.assertRaises(IOError, open, '/path/to/error_file', 'r')

        # Reset open's side effect and check read/write side effects.
        mock_open['/path/to/error_file'].side_effect = None
        mock_open['/path/to/error_file'].read.side_effect = IOError()
        mock_open['/path/to/error_file'].write.side_effect = IOError()
        with open('/path/to/error_file', 'r') as handle:
            self.assertRaises(IOError, handle.read)
            self.assertRaises(IOError, handle.write, 'Bad write')

    def test_hijack_read(self, mock_open):
        """Replace the normal read() with a fake one.

        Replacing the side_effect causes the file's inner state to remain
        unchanged after the call to read().
        """
        mock_open.return_value.read.side_effect = lambda: 'Hijacked!'

        with open('/path/to/file', 'w') as handle:
            contents = handle.read()

        self.assertEqual('Hijacked!', contents)
        self.assertEqual(0, handle.tell())

    def test_hijack_write(self, mock_open):
        """Replace the normal write() with a fake one.

        Replacing the side_effect causes the file's inner state to remain
        unchanged after the call to write().
        """
        def fake_write(data):
            # pylint: disable=missing-docstring
            contents[0] = data

        # If we define contents as a 'simple' variable (just None, for example)
        # the assignment inside fake_write() will assign to a local variable
        # instead of the 'outer' contents variable.
        contents = [None, ]
        mock_open.return_value.write.side_effect = fake_write

        with open('/path/to/file', 'r') as handle:
            handle.write('text')

        self.assertEqual('text', contents[0])
        self.assertEqual(0, handle.tell())

    def test_wrap_read(self, mock_open):
        """Wrap the normal read() function to add to regular operations.

        This is a method of allowing the mock to behave normally while adding
        our own code around operations.
        """
        def wrap_read(original_read):
            # pylint: disable=missing-docstring
            original_side_effect = original_read.side_effect

            @wraps(original_side_effect)
            def wrapped_read(*args, **kws):
                # pylint: disable=missing-docstring
                sentinal[0] = True
                return original_side_effect(*args, **kws)

            original_read.side_effect = wrapped_read

        # Avoid uninitialized assignment (see test_hijack_write()).
        sentinal = [False, ]
        mock_open.return_value.read_data = 'Some text'
        wrap_read(mock_open.return_value.read)

        with open('/path/to/file', 'w') as handle:
            contents = handle.read()

        self.assertEqual('Some text', contents)
        self.assertTrue(sentinal[0])

    def test_wrap_write(self, mock_open):
        """Wrap the normal write() function to add to regular operations.

        This is a method of allowing the mock to behave normally while adding
        our own code around operations.
        """
        def wrap_write(original_write):
            # pylint: disable=missing-docstring
            original_side_effect = original_write.side_effect

            @wraps(original_side_effect)
            def wrapped_write(*args, **kws):
                # pylint: disable=missing-docstring
                sentinal[0] = True
                return original_side_effect(*args, **kws)

            original_write.side_effect = wrapped_write

        # Avoid uninitialized assignment (see test_hijack_write()).
        sentinal = [False, ]
        wrap_write(mock_open.return_value.write)

        with open('/path/to/file', 'w') as handle:
            handle.write('Some text')

        self.assertEqual('Some text', handle.read_data)
        self.assertTrue(sentinal[0])

    def test_multiple_files(self, mock_open):
        """Test different side effects for different files."""
        mock_open['fail_on_open'].side_effect = IOError()
        mock_open['fail_on_read'].read.side_effect = IOError()
        mock_open['fail_on_write'].write.side_effect = IOError()

        with open('success', 'w') as handle:
            handle.write('some text')

        self.assertRaises(IOError, open, 'fail_on_open', 'rb')

        with open('fail_on_read', 'r') as handle:
            self.assertRaises(IOError, handle.read)

        with open('fail_on_write', 'w') as handle:
            self.assertRaises(IOError, handle.write, 'not to be written')

        with open('success', 'r') as handle:
            self.assertEqual('some text', handle.read())


class TestAPI(unittest.TestCase):
    """Test conformance to mock library's API."""
    def test_read_data(self):
        """Check passing of `read_data` to the constructor."""
        mock_open = MockOpen(read_data='Data from the file')

        with patch(OPEN, mock_open):
            with open('/path/to/file', 'r') as handle:
                contents = handle.read()

        self.assertEqual('Data from the file', contents)

    def test_reset_mock(self):
        """Check that reset_mock() works."""
        # Reset globally for all file mocks.
        mock_open = MockOpen(read_data='Global')
        mock_open['/path/to/file'].read_data = 'File-specific'
        mock_open.reset_mock()

        with patch(OPEN, mock_open):
            with open('/path/to/file', 'r') as handle:
                self.assertEqual('', handle.read())

        # Reset a for a specific file mock.
        mock_open = MockOpen(read_data='Global')
        mock_open['/path/to/file'].read_data = 'File-specific'
        mock_open['/path/to/file'].reset_mock()

        with patch(OPEN, mock_open):
            with open('/path/to/file', 'r') as handle:
                self.assertEqual('', handle.read())

            with open('/path/to/other/file', 'r') as handle:
                self.assertEqual('Global', handle.read())
