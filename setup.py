#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    with open(filename) as f:
        lineiter = [line.strip() for line in f]
    return [line for line in lineiter if line and not line.startswith("#")]

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = parse_requirements("requirements.txt")

test_requirements = parse_requirements("requirements_dev.txt")

setup(
    name='vangare',
    version='0.1.0',
    description="Python XMPP Server",
    long_description=readme + '\n\n' + history,
    author="María Ten Rodríguez",
    author_email='materod@upv.edu.es',
    url='https://github.com/materod-upv/vangare',
    python_requires='>=3.8',
    packages=find_packages(include=['vangare', 'vangare.*']),
    entry_points={
        'console_scripts': [
            'vangare=vangare.cli:main',
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='vangare',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Internet :: XMPP',
    ],
    test_suite='tests',
    tests_require=test_requirements,
)
