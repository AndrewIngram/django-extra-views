Installation
------------

Install the stable release from pypi (using pip):

.. code-block:: sh

    pip install django-extra-views

Or install the current master branch from github:

.. code-block:: sh

    pip install -e git://github.com/AndrewIngram/django-extra-views.git#egg=django-extra-views

Then add ``'extra_views'`` to your ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'extra_views',
        ...
    ]
