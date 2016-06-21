# setup.py
from setuptools import setup

setup(
    name='sad sound app',
    version='1.0',
    py_modules=['player'],
    install_requires=['Click',
      'soundcloud'],
    entry_points='''
    [console_scripts]
    sady=player:cli
    '''
)
