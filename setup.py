#!/usr/bin/env python
from distutils.core import setup

setup(
    name = 'mouse_driver',
    version = '0.0.1',
    author = 'Paul Milliken',
    author_email = 'paul.milliken@gmail.com',
    scripts = ['src/simple_mouse_driver.py'],
    packages = ['mouse_driver'],
    package_dir={'':'src'}
)
