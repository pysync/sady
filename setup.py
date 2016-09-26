#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('sady/cli.py').read(),
    re.M
).group(1)

# enjoy commandline use for search and play
# any music available in soundclound
setup(
    name='sady',
    version=version,
    author='Dung Nguyen Tri',
    author_email='dungntnew@gmail.com',
    description=u'A cmd soundclound player (๑˃̵ᴗ˂̵)',
    license='MIT',
    keywords='cmd, terminal, soundclound, music, player',
    url='https://github.com/dungntnew/sady',
    long_description='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
    packages=find_packages(),
    include_package_data=True,
    test_suite='tests',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'sady = sady.cli:start'
        ]
    }
)
