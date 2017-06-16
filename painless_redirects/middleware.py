# coding: utf-8
from __future__ import unicode_literals

from django.conf import settings
from django import http
from django.utils.encoding import force_text
from django.utils.http import urlquote
from django.contrib.sites.models import Site

from .models import Redirect


class ForceSiteDomainRedirectMiddleware(object):
    """
    redirect to the main domain, if not yet there.
    do nothing if settings.DEBUG
    """
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
    def process_request(self, request):
        """
        if a domain redirect is found...redirect
        mostly used by "domain collectors"
        """
        host = request.get_host()
        current_site = Site.objects.get_current()
        if host == current_site.domain:
            return None
        redirect = None
        # better match?
        redirect = Redirect.objects.filter(domain=host, old_path=request.path)
        # only domain. redirect anyway!
        if not redirect.count():
            redirect = Redirect.objects.filter(domain=host)
        if redirect.count():
            new_uri = '%s://%s%s' % (
                request.is_secure() and 'https' or 'http',
                redirect.redirect_value()
            )
            return http.HttpResponsePermanentRedirect(new_uri)

    def process_response(self, request, response):
        """
        if 404, and there is a redirect...
        """
        if response.status_code != 404:
            # No need to check for a redirect for non-404 responses.
            return response
        # TODO: this exception code looks like mess. and not DRY
        # TODO: handle orm.get with multiple objects returned!
        current_site = Site.objects.get_current()
        current_path = force_text(request.path)
        if request.META.get('QUERY_STRING', None):
            current_path += '?' + force_text(request.META.get('QUERY_STRING'))
        redirect = None
        # exact match of path and site. yay.
        redirect = Redirect.objects.filter(
            old_path=current_path, site=current_site)
        # wildcard match, with matching site
        if not redirect.count():
            remaining_path, rubbish = current_path.rsplit("/", 1)
            right_path = ""
            while remaining_path:
                redirect = Redirect.objects.filter(
                    old_path=remaining_path + "/", wildcard_match=True,
                    site=current_site)
                if redirect.count():
                    break
                remaining_path, right_side = remaining_path.rsplit("/", 1)
                right_path = "%s/%s" % (right_side, right_path)
        # exact path match
        if not redirect.count():
            redirect = Redirect.objects.filter(old_path=current_path, site=None)
        # wildcard match
        if not redirect.count():
            remaining_path, rubbish = current_path.rsplit("/", 1)
            right_path = ""
            while remaining_path:
                redirect = Redirect.objects.filter(
                    old_path=remaining_path + "/", wildcard_match=True, site=None)
                if redirect.count():
                    break
                remaining_path, right_side = remaining_path.rsplit("/", 1)
                right_path = '%s/%s' % (right_side, right_path)
        if redirect.count():
            to_redirect = redirect[0].redirect_value()
            # TODO: if domain was set, add schema (https/http)
            return http.HttpResponsePermanentRedirect(to_redirect)
        return response
