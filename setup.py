from setuptools import setup, find_packages

setup(
    name='python-textile',
    version='2.1.3',
    description='Make type not look like crap (for django apps)',
    author='Mark Pilgrim, Roberto A. F. De Almeida, Alex Shiels, Jason Samsa, Chris Drackett',
    author_email='chris@shelfworthy.com',
    url='http://github.com/chrisdrackett/python-textile',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 1',
        'Environment :: Web Environment',
        'Intended Audience :: Developers :: Designers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)