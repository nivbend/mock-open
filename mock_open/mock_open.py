from mock import Mock, NonCallableMock
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class FileLikeMock(NonCallableMock):
    """Acts like a file object returned from open()."""
    def __init__(self, read_data="", *args, **kws):
        kws.update({"spec": file, })
        super(FileLikeMock, self).__init__(*args, **kws)
        self.__is_closed = False
        self.read_data = read_data

    @property
    def closed(self):
        return self.__is_closed

    @property
    def read_data(self):
        return self.__contents.getvalue()

    @read_data.setter
    def read_data(self, contents):
        self.__contents = StringIO()

        # Constructing a cStrinIO object with the input string would result
        # in a read-only object, so we write the contents after construction.
        self.__contents.write(contents)

        # Set tell/read/write/etc side effects to access the new contents
        # object.
        self.tell.side_effect = self.__contents.tell
        self.read.side_effect = self.__contents.getvalue
        self.write.side_effect = self.__contents.write
        self.close.side_effect = self._close

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception, traceback):
        self.close()

    def reset_mock(self, visited=None):
        """Reset the default tell/read/write/etc side effects."""
        super(FileLikeMock, self).reset_mock(visited)

        # Reset contents and tell/read/write/close side effects.
        self.read_data = ""

    def _close(self):
        self.__is_closed = True


class MockOpen(Mock):
    def __init__(self, read_data="", *args, **kws):
        kws.update({"spec": open, "name": open.__name__, })
        super(MockOpen, self).__init__(*args, **kws)
        self.__files = {}
        self.__read_data = read_data

    def __call__(self, path, mode="r", *args, **kws):
        if path in self.__files:
            self.return_value = self.__files[path]
            self.side_effect = self.return_value.side_effect

        child = super(MockOpen, self).__call__(path, mode, *args, **kws)
        child.name = path
        # pylint: disable=attribute-defined-outside-init
        child.mode = mode

        if path not in self.__files:
            self.__files[path] = child

        return child

    def __getitem__(self, path):
        return self.__files.setdefault(path, FileLikeMock())

    def __setitem__(self, path, value):
        value.__enter__ = lambda self: self
        value.__exit__ = lambda self, *args: None
        self.__files[path] = value

    def _get_child_mock(self, **kws):
        kws.update({"read_data": self.__read_data, })
        return FileLikeMock(**kws)
