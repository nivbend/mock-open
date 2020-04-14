"""Setuptools setup script for the package."""

from setuptools import setup, find_packages
import sys


def _get_version():
    # pylint: disable=missing-docstring
    with open('.version') as version:
        return version.read().rstrip("\n")

def _get_description():
    # pylint: disable=missing-docstring
    with open('README.md') as readme:
        return readme.read()

DEPENDENCIES = []
if sys.version_info < (3, 3):
    DEPENDENCIES.append('mock')


setup(
    name='mock-open',
    version=_get_version(),
    description='A better mock for file I/O',
    long_description=_get_description(),
    long_description_content_type='text/markdown',
    url='http://github.com/nivbend/mock-open',
    author='Niv Ben-David',
    author_email='nivbend@gmail.com',
    license='MIT',
    packages=find_packages('src'),
    package_dir={ '': 'src', },
    test_suite='mock_open.test',
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
        'Programming Language :: Python :: 3',
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
