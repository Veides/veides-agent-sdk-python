#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='veides-agent-sdk',
    version='0.1.0',
    description='Agent Python SDK for Veides',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/veides/veides-agent-sdk-python',
    author='Veides Team',
    author_email='contact@veides.io',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Communications',
        'Topic :: Home Automation',
        'Topic :: Software Development',
        'Topic :: Software Development :: Embedded Systems',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=[
        'paho-mqtt==1.5.1',
    ],
)
