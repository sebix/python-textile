from setuptools import setup, find_packages
import sys

version = '2.1.5'

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name='textile',
    version=version,
    description='Textile processing for python.',
    author='Chris Drackett',
    author_email='chris@chrisdrackett.com',
    url='http://github.com/chrisdrackett/python-textile',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='textile,text',
    test_suite = 'nose.collector',
    tests_require = ['nose'],
    include_package_data=True,
    zip_safe=False,
    **extra
)
