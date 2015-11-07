"""Setuptools setup script for the package."""

from setuptools import setup
import sys


def _get_version():
    # pylint: disable=missing-docstring
    with open('.version') as version:
        return version.read().rstrip("\n")

DEPENDENCIES = []
if sys.version_info < (3, 3):
    DEPENDENCIES.append('mock')


setup(
    name='mock-open',
    version=_get_version(),
    description='A better mock for file I/O',
    url='http://github.com/nivbend/mock-open',
    author='Niv Ben-David',
    author_email='nivbend@gmail.com',
    license='MIT',
    packages=['mock_open', ],
    test_suite='mock_open.test.test_mocks',
    install_requires=DEPENDENCIES,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords=' '.join([
        'testing',
        'unittest',
        'test',
        'mock',
        'mocking',
        'patch',
        'patching',
        'stubs',
        'fakes',
        'doubles'
    ]),
    )
