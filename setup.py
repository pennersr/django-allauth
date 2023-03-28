#!/usr/bin/env python
from __future__ import print_function

import io

from setuptools import find_packages, setup

long_description = io.open("README.rst", encoding="utf-8").read()

# Dynamically calculate the version based on allauth.VERSION.
version = __import__("allauth").__version__

METADATA = dict(
    name="django-allauth",
    version=version,
    author="Raymond Penners",
    author_email="raymond.penners@intenct.nl",
    description="Integrated set of Django applications addressing"
    " authentication, registration, account management as well as"
    " 3rd party (social) account authentication.",
    long_description=long_description,
    url="http://www.intenct.nl/projects/django-allauth/",
    keywords="django auth account social openid twitter facebook oauth registration",
    project_urls={
        "Documentation": "https://django-allauth.readthedocs.io/en/latest/",
        "Changelog": "https://github.com/pennersr/django-allauth/blob/main/ChangeLog.rst",
        "Source": "http://github.com/pennersr/django-allauth",
        "Tracker": "https://github.com/pennersr/django-allauth/issues",
        "Donate": "https://github.com/sponsors/pennersr",
    },
    tests_require=[
        "Pillow >= 9.0",
    ],
    install_requires=[
        "Django >= 3.0",
        "python3-openid >= 3.0.8",
        "requests-oauthlib >= 0.3.0",
        "requests",
        "pyjwt[crypto] >= 1.7",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Web Environment",
        "Topic :: Internet",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
    ],
    packages=find_packages(exclude=["example"]),
)

if __name__ == "__main__":
    setup(**METADATA)
