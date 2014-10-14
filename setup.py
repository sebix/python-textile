from setuptools import setup, find_packages
import os
import sys

install_requires = ['regex']

try:
    from collections import OrderedDict
except ImportError:
    install_requires.extend(['ordereddict>=1.1'])

if 'develop' in sys.argv:
    install_requires.extend([
        'tox',
    ])

def get_version():
    basedir = os.path.dirname(__file__)
    with open(os.path.join(basedir, 'textile/version.py')) as f:
        variables = {}
        exec(f.read(), variables)
        return variables.get('VERSION')
    raise RuntimeError('No version info found.')

setup(
    name='textile',
    version=get_version(),
    description='Textile processing for python.',
    url='http://github.com/textile/python-textile',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='textile,text',
    install_requires=install_requires,
    test_suite='nose.collector',
    tests_require=['nose'],
    include_package_data=True,
    zip_safe=False,
)

