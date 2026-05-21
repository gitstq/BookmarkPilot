#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BookmarkPilot Setup Script
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ''

setup(
    name='bookmarkpilot',
    version='1.0.0',
    description='Lightweight Terminal Bookmark Manager - Manage your bookmarks from the command line',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='BookmarkPilot Team',
    author_email='contact@bookmarkpilot.dev',
    url='https://github.com/gitstq/bookmarkpilot',
    packages=find_packages(),
    py_modules=['bookmarkpilot'],
    entry_points={
        'console_scripts': [
            'bookmarkpilot=bookmarkpilot:main',
            'bmp=bookmarkpilot:main',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP :: Browsers',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Utilities',
    ],
    keywords='bookmark manager terminal cli developer productivity tool',
    project_urls={
        'Bug Reports': 'https://github.com/gitstq/bookmarkpilot/issues',
        'Source': 'https://github.com/gitstq/bookmarkpilot',
    },
)
