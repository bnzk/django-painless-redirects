# django painless redirects

[![CI](https://github.com/bnzk/django-painless-redirects/actions/workflows/ci.yml/badge.svg)](https://github.com/bnzk/django-painless-redirects/actions/workflows/ci.yml)
[![PyPi Version](https://img.shields.io/pypi/v/django-painless-redirects.svg "PyPi Version")](https://pypi.python.org/pypi/django-painless-redirects/)
[![Licence](https://img.shields.io/pypi/l/django-painless-redirects.svg "Licence")](https://pypi.python.org/pypi/django-painless-redirects/)

like django.contrib.redirects, on steroids. maybe.


## Features

- simple redirects table, with that bit more flexibility / convenience
    - django sites framework support
    - wildcard matching
    - explicit limit to site/domain
    - explicit redirect to site
    - decide if you want to keep GET vars
    - move complete trees (/old/productXY to /new/productXY, with one redirect, for all products)
- force site domain middleware, that redirects to current site's domain, if not already there

Yet to be done:

- decide if to include GET vars when matching a redirect
- contrib packages with "magic" redirects for django-cms, django-filer -> SEO getting easy.


## Installation

To get the latest stable release from PyPi

    pip install django-painless-redirects

Add ``painless_redirects`` to your ``INSTALLED_APPS``

    INSTALLED_APPS = (
        ...,
        'painless_redirects',
    )

Add the following middlware to MIDDLEWARE, to make basic manual redirects work. 

    painless_redirects.middleware.ManualRedirectMiddleware

As a rule of thumb, you'll add the middleware rather at the end of the list. If
you add it more at the beginning, other redirecting middlewares will 
get priority - for example, you'll not be able to redirect any path 
without having a language slug first, when LocaleMiddleware is before 
our middleware.

If you want to always redirect to the domain name entered in your current site (django.contrib.sites must be installed),
also add this middleware (position is not that important):

    painless_redirects.middleware.ForceSiteDomainRedirectMiddleware


## Compatibility

- django 1.11: should use `django-painless-redirects<0.3.6` (not supported anyway since april 2020)


## Usage

Add and manage your redirects in the django admin panel, under "painless redirects" > "redirects". Check hits, 
check auto created redirects, enable them if needed.


## Settings

- `PAINLESS_REDIRECTS_INDEXED_CHARFIELD_MAX_LENGTH (default: 800)` - needed for mysql (set to ~255). forces you to add `'painless_redirects'` to `settings.MIGRATION_MODULES`
- `PAINLESS_REDIRECTS_AUTO_CREATE (default: True)` - auto create redirects when a 404 is encountered
- `PAINLESS_REDIRECTS_AUTO_CREATE_ENABLED (default: False)` - should auto created redirects be enabled instantly? beware, enabling this feature might ruin your SEO, but could also be a real timesaver...
- `PAINLESS_REDIRECTS_AUTO_CREATE_TO_PATH (default: '/')` - where to redirect to, when a 404 is auto created
- `PAINLESS_REDIRECTS_AUTO_CREATE_SITE (default: True)` - limit auto created redirects to the current site (from the django sites framework)


## Development

- there is test app, available with `./manage.py runserver`.
- quick tests, within your current env: ./manage.py test
- to run tests with django 1.11 / 2.0 / 2.1 / ... : `tox`


## Contributions

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
