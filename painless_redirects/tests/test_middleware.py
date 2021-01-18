# coding: utf-8

# dont add this, request.path is non unicode in python 2.7
# or add it, as request.path shoudl be unicode anyway?!
# from __future__ import unicode_literals
from ..models import Redirect

try:
    reload
except NameError:
    from importlib import reload

from django.contrib.sites.models import Site
from django.http import QueryDict
from django.test import TestCase
from django.test import override_settings
from mock import Mock

from painless_redirects import conf
from ..middleware import ManualRedirectMiddleware, ForceSiteDomainRedirectMiddleware


no_auto_create = override_settings(
    PAINLESS_REDIRECTS_AUTO_CREATE=False,
)
auto_create = override_settings(
    PAINLESS_REDIRECTS_AUTO_CREATE=True,
)


class ForceSiteDomainRedirectMiddlewareTestCase(TestCase):

    def setUp(self):
        self.middleware = ForceSiteDomainRedirectMiddleware()
        self.request = Mock()
        self.request.is_secure = lambda: False
        self.request.get_host = lambda: "nogood.com"
        self.request.META = {}
        self.request.GET = QueryDict("")
        self.request.path = "/"

    def test_no_redirect(self):
        self.request.get_host = lambda: "example.com"
        response = self.middleware.process_request(self.request)
        self.assertEqual(response, None)

    def test_debug_no_redirect(self):
        with self.settings(DEBUG=True):
            response = self.middleware.process_request(self.request)
            self.assertEqual(response, None)

    def test_must_redirect(self):
        response = self.middleware.process_request(self.request)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "http://example.com/")

    def test_must_redirect_preserves_path(self):
        self.request.path = "/abc/def/yeah/"
        response = self.middleware.process_request(self.request)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "http://example.com/abc/def/yeah/")

    def test_must_redirect_preserves_getvars(self):
        self.request.path = "/abc/def/yeah/"
        self.request.GET = QueryDict("karma=true")
        response = self.middleware.process_request(self.request)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "http://example.com/abc/def/yeah/?karma=true")


class ManualRedirectMiddlewareTestCase(TestCase):
    """
    request.get_current_site() is always the default example.com fixture
    check: http://blog.namis.me/2012/05/13/writing-unit-tests-for-django-middleware/
    """
    def setUp(self):
        self._setup_request_response_middleware()
        self.redirect = Redirect.objects.create(
            old_path="/the-old-path/",
            new_path="/the-new-path/",
        )
        self.site = Site.objects.create(
            name="example site 1",
            domain="example1.com",
        )
        self.site2 = Site.objects.create(
            name="example site 2",
            domain="example2.com",
        )

    def _setup_request_response_middleware(self):
        self.middleware = ManualRedirectMiddleware()
        self.request = Mock()
        self.request.META = {}
        self.request.get_host = lambda: 'host.com'
        self.response = Mock()

    def test_no_404_on_status_200(self):
        self.request.path = self.redirect.old_path
        self.response.status_code = 200
        self.assertEqual(
            self.middleware.process_response(self.request, self.response),
            self.response)

    @no_auto_create
    def test_no_redirect_found(self):
        reload(conf)
        self.request.path = "/some-other-path/"
        self.response.status_code = 404
        self.assertEqual(
            self.middleware.process_response(self.request, self.response),
            self.response)
        self.assertEqual(1, Redirect.objects.all().count())

    @no_auto_create
    def test_no_redirect_when_site_specified(self):
        reload(conf)
        self.redirect.site = self.site
        self.redirect.save()
        self.request.path = self.redirect.old_path
        self.response.status_code = 404
        self.assertEqual(
            self.middleware.process_response(self.request, self.response),
            self.response)
        self.assertEqual(1, Redirect.objects.all().count())

    def test_simple_redirect(self):
        reload(conf)
        self.response.status_code = 404
        self.request.path = self.redirect.old_path
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "/the-new-path/")

    def test_simple_redirect_302(self):
        reload(conf)
        self.redirect.permanent = False
        self.redirect.save()
        self.response.status_code = 404
        self.request.path = self.redirect.old_path
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/the-new-path/")
        self.redirect.refresh_from_db()
        self.assertEqual(self.redirect.total_hits(), 1)
        self.middleware.process_response(self.request, self.response)
        self.middleware.process_response(self.request, self.response)
        self.redirect.refresh_from_db()
        self.assertEqual(self.redirect.total_hits(), 3)

    def test_redirect_not_enabled(self):
        reload(conf)
        self.redirect.permanent = False
        self.redirect.enabled = False
        self.redirect.save()
        self.response.status_code = 404
        self.request.path = self.redirect.old_path
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 404)
        self.redirect.refresh_from_db()
        self.assertEqual(self.redirect.total_hits(), 1)
        self.middleware.process_response(self.request, self.response)
        self.middleware.process_response(self.request, self.response)
        self.redirect.refresh_from_db()
        self.assertEqual(self.redirect.total_hits(), 3)

    def test_simple_redirect_keep_querystring(self):
        self.response.status_code = 404
        self.request.path = self.redirect.old_path
        self.request.META['QUERY_STRING'] = 'a=b'
        self.redirect.keep_querystring = True
        self.redirect.old_path += "?a=b"
        self.redirect.save()
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "/the-new-path/?a=b")

    def test_simple_redirect_drop_querystring(self):
        self.response.status_code = 404
        self.request.path = self.redirect.old_path
        self.request.META['QUERY_STRING'] = 'a=xy'
        self.redirect.old_path += "?a=xy"
        self.redirect.save()
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "/the-new-path/")

    @auto_create
    def test_wildcard_should_work_with_existing_auto_created_that_is_disabled(self):
        """
        jap. it should!
        :return:
        """
        reload(conf)
        old_path = '/the-old-path/'
        self.response.status_code = 404
        self.request.path = '{}{}'.format(old_path, 'wildcard/maybe/')
        self.redirect.enabled = False
        self.redirect.save()
        self.assertEqual(Redirect.objects.filter(enabled=True).count(), 0)
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Redirect.objects.all().count(), 2)  # auto created one!
        # the auto redirects
        self.redirect.enabled = True
        self.redirect.save()
        self.assertEqual(Redirect.objects.filter(enabled=True).count(), 1)
        # with existing auto created redirect!
        self.redirect.wildcard_match = True
        self.redirect.enabled = True
        self.redirect.save()
        self._setup_request_response_middleware()
        self.response.status_code = 404
        self.request.path = '{}{}'.format(self.redirect.old_path, 'wildcard/maybe/')
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual("/the-new-path/", response.url, )
        self.assertEqual(Redirect.objects.count(), 2)

    @no_auto_create
    def test_special_chars_in_url(self):
        """
        in python 2.7, request.path seems to be ascii, in certain deployment scenarios
        only reproducable when not importing from __future__ import unicode_literals
        probably related: https://serverfault.com/questions/359934/unicodeencodeerror-when-uploading-files-in-django-admin
        only happened on a uwsgi configuration for now.
        """
        reload(conf)
        self.response.status_code = 404
        self.request.path = self.redirect.old_path
        self.request.path = "/2011/11/réééédirect/"
        self.request.META['QUERY_STRING'] = "?what=ééé"
        response = self.middleware.process_response(self.request, self.response)
        # only check if it doesnt fail for now.
        self.assertEqual(response.status_code, 404)

    def test_new_site_redirect(self):
        self.redirect.new_site = self.site
        self.redirect.save()
        self.response.status_code = 404
        self.request.scheme = "https"
        self.request.path = "/the-old-path/"
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(
            response.url, "https://%s%s" % (self.redirect.new_site.domain, self.redirect.new_path))

    def test_wildcard_redirect(self):
        self.redirect.old_path = "/the-wildcard/yes/"
        self.redirect.wildcard_match = True
        self.redirect.save()
        self.response.status_code = 404
        self.request.path = "%sthe/right/part/" % self.redirect.old_path
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "/the-new-path/")

    def test_wildcard_redirect_keep_tree(self):
        self.redirect.old_path = "/the-wildcard/yes/"
        self.redirect.wildcard_match = True
        self.redirect.keep_tree = True
        self.redirect.save()
        self.response.status_code = 404
        self.request.path = "%sthe/right/part/" % self.redirect.old_path
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "/the-new-path/the/right/part/")
        # must work with site too
        # self.redirect.site = self.site
        self.redirect.save()
        self._setup_request_response_middleware()  # re-init
        self.response.status_code = 404
        self.request.path = "%sthe/right/part/2" % self.redirect.old_path
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "/the-new-path/the/right/part/2")

    def test_wildcard_redirect_with_site(self):
        self.redirect.site = Site.objects.get_current()
        self.redirect.old_path = "/the-wildcard/yes/"
        self.redirect.wildcard_match = True
        self.redirect.save()
        self.response.status_code = 404
        self.request.path = "%sthe/right/part/" % self.redirect.old_path
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "/the-new-path/")

    def test_redirect_without_slash(self):
        self.redirect.old_path = '/whatever/check.html'
        self.redirect.save()
        self.request.path = self.redirect.old_path
        self.response.status_code = 404
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "/the-new-path/")

    def test_from_custom_domain(self):
        self.redirect.domain = 'custom.com'
        self.redirect.old_path = '/'
        self.redirect.new_path = 'http://another.com/'
        self.redirect.save()
        self.request.path = self.redirect.old_path
        self.request.get_host = lambda: 'custom.com'
        self.response.status_code = 200
        response = self.middleware.process_request(self.request, )
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "http://another.com/")

    def test_from_custom_domain_false_positive(self):
        self.redirect.domain = 'custom.com'
        self.redirect.old_path = '/'
        self.redirect.new_path = 'http://another.com/'
        self.redirect.save()
        self.request.path = self.redirect.old_path
        # check for false positives!
        self.request.get_host = lambda: 'none-or-what.com'
        self.response.status_code = 200
        response = self.middleware.process_request(self.request)
        self.assertEqual(response, None)
        response = self.middleware.process_response(self.request, self.response)
        self.assertNotEqual(response.status_code, 301)
        # self.assertEqual(response.url, "http://another.com/")

    def test_old_path_too_long(self):
        reload(conf)
        very_long = '/'
        for c in range(0, conf.INDEXED_CHARFIELD_MAX_LENGTH):
            very_long += 'ccccc'
        self.assertGreater(len(very_long), conf.INDEXED_CHARFIELD_MAX_LENGTH)
        self.request.path = very_long + "/"
        # check for false positives!
        self.response.status_code = 404
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(404, response.status_code)
        self.assertEqual(2, Redirect.objects.all().count())
        self.assertEqual(conf.INDEXED_CHARFIELD_MAX_LENGTH, len(Redirect.objects.all()[0].old_path))

    @auto_create
    def test_auto_create_with_locale_middleware(self):
        # will be redirected to /en/' by locale middleware later on!
        self.request.path = '/?test'
        self.response.status_code = 404
        self.assertEqual(Redirect.objects.all().count(), 1)
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Redirect.objects.all().count(), 1)

        # 404 with lang slug > auto create ok!
        self.response.status_code = 404
        self.request.path = '/nothing-yet/'
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Redirect.objects.all().count(), 2)

    @auto_create
    def test_auto_create_respect_append_slash(self):
        # will be redirected to /nope/' by locale commonmiddleware later on!
        self.request.path = '/nope'
        self.response.status_code = 404
        self.assertEqual(Redirect.objects.all().count(), 1)
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Redirect.objects.all().count(), 1)

        # 404 with lang slug > auto create ok!
        self.response.status_code = 404
        self.request.path = '/nothing-yet/'
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Redirect.objects.all().count(), 2)
