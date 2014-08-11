from setuptools import setup

setup(
    name='django-extra-views',
    version='0.6.5',
    url='https://github.com/AndrewIngram/django-extra-views',
    install_requires=[
        'Django >=1.3',
        'six==1.5.2',
    ],
    description="Extra class-based views for Django",
    long_description=open('README.rst', 'r').read(),
    license="MIT",
    author="Andrew Ingram",
    author_email="andy@andrewingram.net",
    packages=['extra_views'],
    package_dir={'extra_views': 'extra_views'},
    include_package_data = True,    # include everything in source control
    package_data={'extra_views': ['*.py','contrib/*.py','tests/*.py','tests/templates/*.html', 'tests/templates/extra_views/*.html']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python']
)
