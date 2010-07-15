from setuptools import setup

setup(
    name='python-textile',
    version='2.1.5',
    description='Make type not look like crap (for django apps)',
    author='Mark Pilgrim, Roberto A. F. De Almeida, Alex Shiels, Jason Samsa, Chris Drackett, Kurt Raschke',
    author_email='kurt@kurtraschke.com',
    url='http://github.com/kurtraschke/python-textile',
    packages = [
        "textile",
        "textile.tools",
        "textile.tests",
    ],
    classifiers=[
        'Development Status :: 1',
        'Environment :: Web Environment',
        'Intended Audience :: Developers :: Designers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
    test_suite = 'nose.collector',
    tests_require = ['nose']
)
