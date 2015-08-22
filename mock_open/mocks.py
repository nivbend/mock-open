"""Mock classes for open() and the file type."""

import sys

if sys.version_info < (3, 3):
    from mock import Mock, NonCallableMock
else:
    from unittest.mock import Mock, NonCallableMock

if sys.version_info >= (3, 0):
    from io import TextIOWrapper, StringIO
else:
    from io import TextIOWrapper, BytesIO as StringIO


class FileLikeMock(NonCallableMock):
    """Acts like a file object returned from open()."""
    def __init__(self, name=None, read_data="", *args, **kws):
        kws.update({"spec": TextIOWrapper, })
        super(FileLikeMock, self).__init__(*args, **kws)
        self.__is_closed = False
        self.read_data = read_data
        self.close.side_effect = self._close

        if name is not None:
            self.name = name

    @property
    def closed(self):
        # pylint: disable=missing-docstring
        return self.__is_closed

    @property
    def read_data(self):
        """Bypass read function to access the contents of the file.

        This property should be used for testing purposes.
        """
        return self.__contents.getvalue()

    @read_data.setter
    def read_data(self, contents):
        # pylint: disable=missing-docstring
        # pylint: disable=attribute-defined-outside-init
        self.__contents = StringIO()

        # Constructing a cStrinIO object with the input string would result
        # in a read-only object, so we write the contents after construction.
        self.__contents.write(contents)

        # Set tell/read/write/etc side effects to access the new contents
        # object.
        self.tell.side_effect = self.__contents.tell
        self.seek.side_effect = self.__contents.seek
        self.read.side_effect = self.__contents.read
        self.readline.side_effect = self.__contents.readline
        self.readlines.side_effect = self.__contents.readlines
        self.write.side_effect = self.__contents.write
        self.writelines.side_effect = self.__contents.writelines

    def __enter__(self):
        # Reset the position in buffer (in case we re-opened it).
        self.__contents.seek(0)

        return self

    def __exit__(self, exception_type, exception, traceback):
        self.close()

    def __iter__(self):
        return iter(self.__contents)

    def reset_mock(self, visited=None):
        """Reset the default tell/read/write/etc side effects."""
        # In some versions of the mock library, `reset_mock` takes an argument
        # and in some it doesn't. We try to handle all situations.
        if visited is not None:
            super(FileLikeMock, self).reset_mock(visited)
        else:
            super(FileLikeMock, self).reset_mock()

        # Reset contents and tell/read/write/close side effects.
        self.read_data = ""
        self.close.side_effect = self._close

    def _close(self):
        """Mark file as closed (used for side_effect)."""
        self.__is_closed = True


class MockOpen(Mock):
    """A mock for the open() builtin function."""
    def __init__(self, read_data="", *args, **kws):
        kws.update({"spec": open, "name": open.__name__, })
        super(MockOpen, self).__init__(*args, **kws)
        self.__files = {}
        self.__read_data = read_data

    def _mock_call(self, path, mode="r", *args, **kws):
        original_side_effect = self._mock_side_effect

        if path in self.__files:
            self._mock_return_value = self.__files[path]
            self._mock_side_effect = self._mock_return_value.side_effect

        try:
            child = super(MockOpen, self)._mock_call(path, mode, *args, **kws)
        finally:
            # Reset the side effect after each call so that the next call to
            # open() won't cause the same side_effect.
            self._mock_side_effect = original_side_effect

        # Consecutive calls to open() set `return_value` to the last file mock
        # created. If the paths differ (and child isn't a newly-created mock,
        # evident by its name attribute being unset) we create a new file mock
        # instead of returning to previous one.
        if not isinstance(child.name, Mock) and path != child.name:
            child = self._get_child_mock(name=path)
            self.__files[path] = child

        child.name = path
        # pylint: disable=attribute-defined-outside-init
        child.mode = mode

        if path not in self.__files:
            self.__files[path] = child

        self._mock_return_value = child
        return child

    def __getitem__(self, path):
        return self.__files.setdefault(path, self._get_child_mock(name=path))

    def __setitem__(self, path, value):
        value.__enter__ = lambda self: self
        value.__exit__ = lambda self, *args: None
        self.__files[path] = value

    def reset_mock(self, visited=None):
        # See comment in `FileLikeMock.reset_mock`.
        if visited is not None:
            super(MockOpen, self).reset_mock(visited)
        else:
            super(MockOpen, self).reset_mock()

        self.__files = {}
        self.__read_data = ""

    def _get_child_mock(self, **kws):
        """Create a new FileLikeMock instance.

        The new mock will inherit the parent's side_effect and read_data
        attributes.
        """
        kws.update({
            "_new_parent": self,
            "side_effect": self._mock_side_effect,
            "read_data": self.__read_data,
        })
        return FileLikeMock(**kws)
