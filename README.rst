django painless redirects
============

.. image:: https://travis-ci.org/bnzk/django-painless-redirects.svg
    :target: https://travis-ci.org/bnzk/django-painless-redirects/
.. image:: https://img.shields.io/pypi/v/django-painless-redirects.svg
    :target: https://pypi.python.org/pypi/django-painless-redirects/
.. image:: https://img.shields.io/pypi/l/django-painless-redirects.svg
    :target: https://pypi.python.org/pypi/django-painless-redirects/

like django.contrib.redirects, on steroids. maybe.

Features
------------

- simple redirects table, with that bit more flexibility / convenience
    - wildcard matching
    - explicit limit to site/domain
    - explicit redirect to site
- force site domain middleware, that redirects to current site's domain, if not already there

Yet to be done:
- decide if you want to keep GET vars
- move complete trees
- APPEND_SLASH handling (when trying to redirect /whatever/was-here.html)
- contrib packages with "magic" redirects for django-cms, django-filer -> SEO becoming easy.


Installation & Usage
------------

To get the latest stable release from PyPi

.. code-block:: bash

    pip install django-painless-redirects

Add ``painless_redirects`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'painless_redirects',
    )

Add the following middlware to MIDDLEWARE_CLASSES (1.10 style middlewares will be supported soon),
to make basic redirects work.

.. code-block:: bash

    painless_redirects.middleware.ManualRedirectMiddleware

If you want to be redirected to the domain name entered in your current site (django.contrib.sites must be installed),
also add this middleware:

.. code-block:: bash

    painless_redirects.middleware.ForceSiteDomainRedirectMiddleware


Development
------------

- there is test app, available with `./manage.py runserver`.
- to run tests: ./manage.py test
- to run tests with django 1.8 / 1.9 / 1.10: `tox`


Contributions
-------------

If you want to contribute to this project, please perform the following steps

.. code-block:: bash

    # Fork this repository
    # Clone your fork
    mkvirtualenv django-painless-redirects
    pip install -r test_requirements.txt
    git checkout -b feature_branch
    # Implement your feature and tests
    git add . && git commit
    git push -u origin feature_branch
    # Send us a pull request for your feature branch
