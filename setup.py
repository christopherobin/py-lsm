try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='lsm',
    version='0.1.0',
    description='Object-Oriented wrapper around docker-py',
    author='Christophe Robin',
    author_email='crobin@nekoo.com',
    license='MIT',
    packages=['lsm'],
    test_suite="tests",
)
