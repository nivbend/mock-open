mock-open
=========
[![PyPI version](https://badge.fury.io/py/mock-open.svg)](https://pypi.python.org/pypi/mock-open/)
[![Build Status](https://travis-ci.org/nivbend/mock-open.svg?branch=master)](https://travis-ci.org/nivbend/mock-open)
[![GitHub license](https://img.shields.io/github/license/nivbend/mock-open.svg)](https://github.com/nivbend/mock-open/blob/master/LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/nivbend/mock-open/graphs/commit-activity)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

A better mock for file I/O.

Install
-------

```
$ pip install mock-open
```

class `MockOpen`
--------------

The `MockOpen` class should work as a stand-in replacement for [`mock.mock_open`](http://docs.python.org/3/library/unittest.mock.html#mock-open) with some
added features:
* Multiple file support, including a mapping-like access to file mocks by path:

  ```python
  from mock_open import MockOpen
  mock_open = MockOpen()
  mock_open["/path/to/file"].read_data = "Data from a fake file-like object"
  mock_open["/path/to/bad_file"].side_effect = IOError()
  ```

  You can also configure behavior via the regular `mock` library API:

  ```python
  mock_open = MockOpen()
  mock_open.return_value.write.side_effect = IOError()
  ```

* Persistent file contents between calls to `open`:

  ```python
  with patch("builtins.open", MockOpen()):
      with open("/path/to/file", "w") as handle:
          handle.write("Some text")

      with open("/path/to/file", "r") as handle:
          assert "Some text" == handle.read()
  ```

* All the regular file operations: `read`, `readline`, `readlines`, `write`, `writelines`, `seek`, `tell`.
