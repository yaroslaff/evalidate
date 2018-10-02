from setuptools import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='evalidate',
      version='0.7.5',
      url='http://evalidate.readthedocs.org/',
      author='Yaroslav Polyakov',
      author_email='xenon@sysattack.com',
      license='MIT',
      packages=['evalidate'],
      description = 'Validation and secure evaluation untrusted python expressions',
      long_description = read('README.md'),
      long_description_content_type='text/markdown',
      zip_safe=False)

