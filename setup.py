from setuptools import setup
from importlib.machinery import SourceFileLoader
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()

def get_version(path):
    foo = SourceFileLoader(os.path.basename(path), path).load_module()
    return foo.__version__


setup(name='evalidate',
      version=get_version('evalidate/__init__.py'),
      url='http://github.com/yaroslaff/evalidate',
      author='Yaroslav Polyakov',
      author_email='xenon@sysattack.com',
      license='MIT',
      packages=['evalidate'],
      description='Validation and secure evaluation of untrusted python expressions',
      long_description=read('README.md'),
      long_description_content_type='text/markdown',
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          'Topic :: Utilities',
          "Topic :: Security",
          "Topic :: Software Development :: Interpreters",
      ],
      zip_safe=False)
