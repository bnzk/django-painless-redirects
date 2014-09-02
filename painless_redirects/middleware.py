# coding: utf-8
from django import http
from django.contrib.sites.models import Site

from .models import Redirect


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
        # first try?
        try:
            redirect = Redirect.objects.get(domain=host)
        except Redirect.DoesNotExist:
            pass
        # better match?
        try:
            redirect = Redirect.objects.get(domain=host,
                                     old_path=request.get_full_path())
        except Redirect.DoesNotExist:
            pass
        if redirect is not None:
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
        current_site = Site.objects.get_current()
        current_path = request.get_full_path()
        redirect = None
        try:
            redirect = Redirect.objects.get(old_path=current_path)
        except Redirect.DoesNotExist:
            pass
        try:
            redirect = Redirect.objects.get(old_path=current_path,
                                            site=current_site)
        except Redirect.DoesNotExist:
            pass
        if redirect is not None:
            return http.HttpResponsePermanentRedirect(redirect.new_path)
        return response
