from setuptools import setup

setup(
    name='django-extra-views-ng',
    version='0.3.3',
    url='https://github.com/hovel/django-extra-views',
    description="Extra class-based views for Django",
    long_description=open('README.rst', 'r').read(),
    license="MIT",
    author="Pavel Zhukov",
    author_email="gelios@gmail.com",
    packages=['extra_views'],
    package_dir={'': '.'},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',   
        'Programming Language :: Python']
)
