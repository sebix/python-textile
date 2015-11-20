from setuptools import setup, find_packages
import os
import sys

install_requires = []


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
    extras_require={
        ':python_version=="2.6"': ['ordereddict>=1.1'],
    },
    tests_require=['pytest'],
    include_package_data=True,
    zip_safe=False,
)

