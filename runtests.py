#!/usr/bin/env python
import sys
import logging
from optparse import OptionParser

from django.conf import settings

logging.disable(logging.CRITICAL)


def configure(nose_args=None):
    if not settings.configured:
        settings.configure(
            DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3'}},
            TEMPLATES=[{
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'APP_DIRS': True,
            }],
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'django.contrib.auth',
                'extra_views',
                'extra_views_tests',
            ],
            MIDDLEWARE=[
                'django.middleware.security.SecurityMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.common.CommonMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
                'django.middleware.clickjacking.XFrameOptionsMiddleware',
            ],
            ROOT_URLCONF='extra_views_tests.urls',
            NOSE_ARGS=nose_args
        )


def runtests(*test_args):
    from django_nose import NoseTestSuiteRunner
    runner = NoseTestSuiteRunner()

    if not test_args:
        test_args = ['extra_views_tests']
    num_failures = runner.run_tests(test_args)
    if num_failures:
        sys.exit(num_failures)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--with-coverage', dest='coverage', default=False,
                      action='store_true')
    parser.add_option('--with-xunit', dest='xunit', default=False,
                      action='store_true')
    parser.add_option('--with-spec', dest='with_spec', default=False,
                      action='store_true')
    parser.add_option('--pdb', dest='pdb', default=False,
                      action='store_true')
    options, args = parser.parse_args()

    nose_args = []
    if options.pdb:
        nose_args.append('--pdb')

    if options.coverage:
        # Nose automatically uses any options passed to runtests.py, which is
        # why the coverage trigger uses '--with-coverage' and why we don't need
        # to explicitly include it here.
        nose_args.extend([
            '--cover-package=extra_views', '--cover-branch', '--cover-html', '--cover-html-dir=htmlcov'])
    configure(nose_args)
    runtests()
