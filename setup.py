#!/usr/bin/env python
from setuptools import setup,find_packages

METADATA = dict(
    name='django-allauth',
    version='0.3.0',
    author='Raymond Penners',
    author_email='raymond.penners@intenct.nl',
    description='Integrated set of Django applications addressing authentication, registration, account management as well as 3rd party (social) account authentication.',
    long_description=open('README.rst').read(),
    url='http://github.com/pennersr/django-allauth',
    keywords='django auth account social openid twitter facebook oauth registration',
    install_requires=['django', 
                      'oauth2', 
                      'python-openid',
                      'django-email-confirmation',
                      'django-uni-form'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Web Environment',
        'Topic :: Internet',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    packages=find_packages(),
    package_data={'allauth': ['templates/allauth/*.html', 
                              'facebook/templates/facebook/*.html' ] }
)

if __name__ == '__main__':
    setup(**METADATA)
    
