from setuptools import setup, find_packages
import os
import sys

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
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='textile,text,html markup',
    install_requires=['six',],
    extras_require={
        ':python_version=="2.6"': ['ordereddict>=1.1'],
        'develop': ['regex', 'pytest', 'pytest-cov'],
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov'],
    include_package_data=True,
    zip_safe=False,
)

