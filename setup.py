from setuptools import setup

setup(
    name='django-extra-views',
    version='0.2.4',
    url='https://github.com/AndrewIngram/django-extra-views',
    install_requires=[
        'Django >=1.3',
    ],
    description="Extra class-based views for Django",
    long_description=open('README.rst', 'r').read(),
    license="MIT",
    author="Andrew Ingram",
    author_email="andy@andrewingram.net",
    packages=['extra_views'],
    package_dir={'': '.'},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python']
)
