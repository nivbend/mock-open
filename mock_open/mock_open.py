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
        self.__contents = StringIO()
        self.__is_closed = False

        # Constructing a cStrinIO object with the input string would result
        # in a read-only object, so we write the contents after construction.
        self.__contents.write(read_data)

        # Set tell/read/write/etc side effects to defaults.
        self.reset_mock()

    @property
    def closed(self):
        return self.__is_closed

    @property
    def read_data(self):
        return self.__contents.getvalue()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception, traceback):
        self.close()

    def reset_mock(self, visited=None):
        """Reset the default tell/read/write/etc side effects."""
        super(FileLikeMock, self).reset_mock(visited)

        self.tell.side_effect = self.__contents.tell
        self.read.side_effect = self.__contents.getvalue
        self.write.side_effect = self.__contents.write
        self.close.side_effect = self._close

    def _close(self):
        self.__is_closed = True


class MockOpen(Mock):
    def __init__(self, *args, **kws):
        kws.update({"spec": open, "name": open.__name__, })
        super(MockOpen, self).__init__(*args, **kws)
        self.__read_data = ""

    def __call__(self, path, mode="r", *args, **kws):
        child = super(MockOpen, self).__call__(path, mode, *args, **kws)
        child.name = path
        # pylint: disable=attribute-defined-outside-init
        child.mode = mode
        return child

    @property
    def read_data(self):
        return self.__read_data

    @read_data.setter
    def read_data(self, data):
        self.__read_data = data

    def _get_child_mock(self, **kws):
        return FileLikeMock(read_data=self.__read_data, **kws)
