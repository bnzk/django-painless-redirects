# coding: utf-8
from __future__ import unicode_literals

from django.conf import settings
from django import http
from django.utils.encoding import force_text
from django.utils.http import urlquote
from django.contrib.sites.models import Site

from .models import Redirect
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
        # match?
        redirect = Redirect.objects.filter(enabled=True, domain=host, old_path=request.path)
        # only domain. redirect anyway!
        if not redirect.count():
            redirect = Redirect.objects.filter(enabled=True, domain=host)
        if redirect.count():
            new_uri = redirect[0].redirect_value(request.scheme)
            # hits
            redirect[0].hits += 1
            redirect[0].save()
            return http.HttpResponsePermanentRedirect(new_uri)

    def process_response(self, request, response):
        """
        if 404, and there is a redirect...
        """
        if response.status_code != 404:
            # No need to check for a redirect for non-404 responses.
            return response
        host = request.get_host()
        current_site = Site.objects.get_current()
        current_path = force_text(request.path)
        querystring = request.META.get('QUERY_STRING', None)
        if querystring:
            current_path += '?' + force_text(querystring)
        current_path = current_path[:conf.INDEXED_CHARFIELD_MAX_LENGTH]
        # path and domain!
        redirects_all, right_path = self._check_for_redirect(current_path, **{'domain': host, })
        redirects_enabled = redirects_all.filter(enabled=True)
        # exact match of path and site.
        if not redirects_enabled.count():
            kwargs = {'site': current_site, 'domain': '', }
            redirects_all, right_path = self._check_for_redirect(current_path, **kwargs)
            redirects_enabled = redirects_all.filter(enabled=True)
        # exact path match
        if not redirects_enabled.count():
            kwargs = {'site': None, 'domain': '', }
            redirects_all, right_path = self._check_for_redirect(current_path, **kwargs)
            redirects_all.filter(enabled=True)
        # not one redirect found > create auto redirect!
        if not redirects_all.count() and conf.AUTO_CREATE:
            the_site = current_site if conf.AUTO_CREATE_SITE else None
            kwargs = {
                'old_path': current_path,
                'auto_created': True,
                # site also via settings?
                'site': the_site,
                'enabled': conf.AUTO_CREATE_ENABLED,
                'new_path': conf.AUTO_CREATE_TO_PATH,
            }
            r = Redirect(**kwargs)
            r.save()
            if conf.AUTO_CREATE_ENABLED:
                redirects_all = [r]
        if len(redirects_all):
            enabled_redirect = None
            for r in redirects_all:
                # hits
                r.hits += 1
                r.save()
                if r.enabled and not enabled_redirect:
                    enabled_redirect = r
            if enabled_redirect:
                new_uri = enabled_redirect.redirect_value(
                    request.scheme,
                    right_path=right_path,
                    querystring=querystring,
                )
                if enabled_redirect.permanent:
                    return http.HttpResponsePermanentRedirect(new_uri)
                else:
                    return http.HttpResponseRedirect(new_uri)
        return response

    def _check_for_redirect(self, path, **kwargs):
        redirect = Redirect.objects.filter(old_path=path, **kwargs)
        right_path = ""
        # wildcard match
        if not redirect.count():
            remaining_path, rubbish = path.rsplit("/", 1)
            while remaining_path:
                redirect = Redirect.objects.filter(
                    old_path=remaining_path + "/", wildcard_match=True, **kwargs)
                if redirect.count():
                    break
                remaining_path, right_side = remaining_path.rsplit("/", 1)
                right_path = '%s/%s' % (right_side, right_path)
            # print("---")
            # print(remaining_path)
            # print(right_path)
        return redirect, right_path
