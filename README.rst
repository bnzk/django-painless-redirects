django painless redirects
============

.. image:: https://travis-ci.org/bnzk/django-painless-redirects.svg
    :target: https://travis-ci.org/bnzk/django-painless-redirects

FAIR WARNING: dont take anything for real that is written below the lines just below, as most (or all) of it
is boilerplate text from https://github.com/bitmazk/django-reusable-app-template (that is great, btw).

like django.contrib.redirects on steroids. maybe.

planned (note to self):

- simple redirects table, with that bit more flexibility
- contrib packages with "magic" redirects for django-cms and django-folderless, SEO ftw.
- contrib package "force_site_domain"

more not to self:

- not forget APPEND_SLASH (when trying to redirect /whatever/was-here.html)
- more?

Development
-----------
there is test app, available with ./manage.py runserver. to run tests: ./manage.py test

Installation
------------

To get the latest stable release from PyPi

.. code-block:: bash

    pip install django-painless-redirects

To get the latest commit from GitHub

.. code-block:: bash

    pip install -e git+git://github.com/benzkji/django-painless-redirects.git#egg=painless_redirects

TODO: Describe further installation steps (edit / remove the examples below):

Add ``painless_redirects`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'painless_redirects',
    )

Add the ``painless_redirects`` URLs to your ``urls.py``

.. code-block:: python

    urlpatterns = patterns('',
        ...
        url(r'^app-url/', include('painless_redirects.urls')),
    )

Before your tags/filters are available in your templates, load them by using

.. code-block:: html

	{% load painless_redirects_tags %}


Don't forget to migrate your database

.. code-block:: bash

    ./manage.py migrate painless_redirects


Usage
-----

TODO: Describe usage or point to docs. Also describe available settings and
templatetags.


Contribute
----------

If you want to contribute to this project, please perform the following steps

.. code-block:: bash

    # Fork this repository
    # Clone your fork
    mkvirtualenv -p python2.7 django-painless-redirects
    make develop

    git co -b feature_branch master
    # Implement your feature and tests
    git add . && git commit
    git push -u origin feature_branch
    # Send us a pull request for your feature branch
