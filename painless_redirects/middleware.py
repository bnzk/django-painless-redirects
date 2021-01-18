# coding: utf-8
from __future__ import unicode_literals

from django.conf import settings
from django import http
from django.utils.encoding import force_text
from django.utils.http import urlquote
from django.contrib.sites.models import Site

from .models import Redirect, RedirectHit
from . import conf


class ForceSiteDomainRedirectMiddleware(object):
    """
    redirect to the main domain, if not yet there.
    do nothing if settings.DEBUG
    """

    def __init__(self, get_response=None):
        if get_response:
            self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        a_possible_redirect = self.process_request(request)
        if a_possible_redirect:
            return a_possible_redirect
        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.
        return response

    def process_request(self, request):
        if settings.DEBUG:
            return None
        host = request.get_host()
        site = Site.objects.get_current()
        if host == site.domain:
            return None
        new_uri = '%s://%s%s%s' % (
            request.is_secure() and 'https' or 'http',
            site.domain,
            urlquote(request.path),
            len(request.GET) > 0 and '?%s' % request.GET.urlencode() or ''
        )
        return http.HttpResponsePermanentRedirect(new_uri)


class ManualRedirectMiddleware(object):

    def __init__(self, get_response=None):
        if get_response:
            self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        a_possible_redirect = self.process_request(request)
        if a_possible_redirect:
            return a_possible_redirect
        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.
        return self.process_response(request, response)

    def process_request(self, request):
        """
        if a domain redirect is found...redirect
        mostly used by "domain collectors"
        -
        in the future, this shoudl only be enforced for redirects with a new field
        "force for non 404s" set to True. (domain field enforces this magically, for now)
        """
        host = request.get_host()
        current_site = Site.objects.get_current()
        if host == current_site.domain:
            return None
        # TODO: refactor with _check_redirect!
        redirects = Redirect.objects.filter(enabled=True, domain=host, old_path=request.path)
        # only domain. redirect anyway!
        if not redirects.count():
            redirects = Redirect.objects.filter(enabled=True, domain=host)
        if redirects.count():
            new_uri = redirects[0].redirect_value(request.scheme)
            # hits
            # redirect[0].hits += 1
            # redirect[0].save()
            referer = request.META.get('HTTP_REFERER', conf.REFERER_NONE_VALUE)
            referer = referer[:conf.INDEXED_CHARFIELD_MAX_LENGTH]
            for redirect in redirects:
                hit, created = RedirectHit.objects.get_or_create(referer=referer, redirect=redirect)
                hit.hits += 1
                hit.save()
            return http.HttpResponsePermanentRedirect(new_uri)

    def process_response(self, request, response):
        """
        if 404, and there is a redirect...
        """
        if response.status_code != 404:
            # No need to check for a redirect for non-404 responses.
            return response
        # prepare basics
        host = request.get_host()
        current_site = Site.objects.get_current()
        current_path = force_text(request.path)
        current_path_only = current_path
        querystring = request.META.get('QUERY_STRING', None)
        if querystring:
            current_path = '{}?{}'.format(current_path_only, force_text(querystring))
        current_path = current_path[:conf.INDEXED_CHARFIELD_MAX_LENGTH]

        # path and domain
        redirects_all, right_path = self._check_for_redirect(current_path, **{'domain': host, })
        redirects_enabled = redirects_all.filter(enabled=True)
        redirects_all = list(redirects_all)

        # exact match of path and site (and no domain)
        kwargs = {'site': current_site, 'domain': '', }
        more_redirects_all, more_right_path = self._check_for_redirect(current_path, **kwargs)
        if not redirects_enabled.count():
            redirects_enabled = more_redirects_all.enabled()
            right_path = more_right_path
        redirects_all += list(more_redirects_all)

        # exact path match
        kwargs = {'site': None, 'domain': '', }
        more_redirects_all, more_right_path = self._check_for_redirect(current_path, **kwargs)
        if not redirects_enabled.count():
            redirects_enabled = more_redirects_all.enabled()
            right_path = more_right_path
        redirects_all += list(more_redirects_all)

        # not one redirect found > create auto redirect!?
        if not len(redirects_all) and conf.AUTO_CREATE:
            create = True
            if 'django.middleware.locale.LocaleMiddleware' in settings.MIDDLEWARE:
                # no good: redirect create only if starting with lang_code
                # for lang_code, lang_label in settings.LANGUAGES:
                #     if current_path[1:].startswith(lang_code):
                #         create = True
                # solutions for now: no redirect create if /
                if current_path_only == '/':
                    create = False
            if not current_path_only.endswith('/') and settings.APPEND_SLASH:
                create = False
            if create:
                the_site = current_site if conf.AUTO_CREATE_SITE else None
                kwargs = {
                    'old_path': current_path,
                    # site also via settings?
                    'site': the_site,
                    'domain': '',
                }
                r, created = Redirect.objects.get_or_create(**kwargs)
                if created:
                    r.auto_created = True
                    r.new_path = conf.AUTO_CREATE_TO_PATH
                    r.enabled = conf.AUTO_CREATE_ENABLED
                    r.save()
                redirects_all = [r]
                # if conf.AUTO_CREATE_ENABLED:
        if len(redirects_all):
            referer = request.META.get('HTTP_REFERER', conf.REFERER_NONE_VALUE)
            referer = referer[:conf.INDEXED_CHARFIELD_MAX_LENGTH]
            for redirect in redirects_all:
                # hits
                hit, created = RedirectHit.objects.get_or_create(referer=referer, redirect=redirect)
                hit.hits += 1
                hit.save()

        if len(redirects_enabled):
            r = redirects_enabled[0]
            new_uri = r.redirect_value(
                request.scheme,
                right_path=right_path,
                querystring=querystring,
            )
            if r.permanent:
                return http.HttpResponsePermanentRedirect(new_uri)
            else:
                return http.HttpResponseRedirect(new_uri)
        return response

    def _check_for_redirect(self, path, **kwargs):
        """
        check for a redirect, including wildcard mathching
        """
        redirect = Redirect.objects.filter(old_path=path, **kwargs)
        right_path = ""
        # wildcard match
        if not redirect.count():
            if path.endswith('/'):
                remaining_path, rubbish = path.rsplit("/", 1)
            else:
                remaining_path = path
            # print(right_path)
            while remaining_path:
                redirect = Redirect.objects.filter(
                    old_path=remaining_path + "/", wildcard_match=True, **kwargs
                )
                if redirect.count():
                    # TODO:  hit counting is not correct like this!
                    if path.endswith('/'):
                        right_path += "/"
                    break
                remaining_path, right_side_split_off = remaining_path.rsplit("/", 1)
                # print("right_path")
                # print(right_path)
                # print(right_side_split_off)
                # print(remaining_path)
                if right_path:
                    right_path = '%s/%s' % (right_side_split_off, right_path)
                else:
                    right_path = right_side_split_off
            # print("---")
            # print(remaining_path)
            # print(right_path)
        return redirect, right_path
