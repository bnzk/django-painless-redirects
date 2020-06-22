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
from . import factories
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

    def _setup_request_response_middleware(self):
        self.middleware = ManualRedirectMiddleware()
        self.request = Mock()
        self.request.META = {}
        self.request.get_host = lambda: 'host.com'
        self.response = Mock()

    def test_no_404_on_status_200(self):
        obj = factories.RedirectFactory()
        self.request.path = obj.old_path
        self.response.status_code = 200
        self.assertEqual(
            self.middleware.process_response(self.request, self.response),
            self.response)

    @no_auto_create
    def test_no_redirect_found(self):
        reload(conf)
        factories.RedirectFactory()
        self.request.path = "/some-other-path/"
        self.response.status_code = 404
        self.assertEqual(
            self.middleware.process_response(self.request, self.response),
            self.response)
        self.assertEqual(1, Redirect.objects.all().count())

    @no_auto_create
    def test_no_redirect_when_site_specified(self):
        reload(conf)
        obj = factories.RedirectFactory()
        obj.site = factories.SiteFactory()
        obj.save()
        self.request.path = obj.old_path
        self.response.status_code = 404
        self.assertEqual(
            self.middleware.process_response(self.request, self.response),
            self.response)
        self.assertEqual(1, Redirect.objects.all().count())

    def test_simple_redirect(self):
        reload(conf)
        obj = factories.RedirectFactory()
        self.response.status_code = 404
        self.request.path = obj.old_path
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "/the-new-path/")

    def test_simple_redirect_302(self):
        reload(conf)
        obj = factories.RedirectFactory()
        obj.permanent = False
        obj.save()
        self.response.status_code = 404
        self.request.path = obj.old_path
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/the-new-path/")
        obj.refresh_from_db()
        self.assertEqual(obj.hits, 1)
        self.middleware.process_response(self.request, self.response)
        self.middleware.process_response(self.request, self.response)
        obj.refresh_from_db()
        self.assertEqual(obj.hits, 3)

    def test_redirect_not_enabled(self):
        reload(conf)
        obj = factories.RedirectFactory()
        obj.permanent = False
        obj.enabled = False
        obj.save()
        self.response.status_code = 404
        self.request.path = obj.old_path
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 404)
        obj.refresh_from_db()
        self.assertEqual(obj.hits, 1)
        self.middleware.process_response(self.request, self.response)
        self.middleware.process_response(self.request, self.response)
        obj.refresh_from_db()
        self.assertEqual(obj.hits, 3)

    def test_simple_redirect_keep_querystring(self):
        obj = factories.RedirectFactory()
        self.response.status_code = 404
        self.request.path = obj.old_path
        self.request.META['QUERY_STRING'] = 'a=b'
        obj.keep_querystring = True
        obj.old_path += "?a=b"
        obj.save()
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "/the-new-path/?a=b")

    def test_simple_redirect_drop_querystring(self):
        obj = factories.RedirectFactory()
        self.response.status_code = 404
        self.request.path = obj.old_path
        self.request.META['QUERY_STRING'] = 'a=xy'
        obj.old_path += "?a=xy"
        obj.save()
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
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 404)
        # the auto redirects
        self.assertEqual(Redirect.objects.count(), 1)
        # with existing auto created redirect!
        wildcard = factories.RedirectFactory()
        wildcard.wildcard_match = True
        wildcard.enabled = True
        wildcard.save()
        self._setup_request_response_middleware()
        self.response.status_code = 404
        self.request.path = '{}{}'.format(wildcard.old_path, 'wildcard/maybe/')
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "/the-new-path/")
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
        obj = factories.RedirectFactory()
        self.response.status_code = 404
        self.request.path = obj.old_path
        self.request.path = "/2011/11/réééédirect/"
        self.request.META['QUERY_STRING'] = "?what=ééé"
        response = self.middleware.process_response(self.request, self.response)
        # only check if it doesnt fail for now.
        self.assertEqual(response.status_code, 404)

    def test_new_site_redirect(self):
        obj = factories.RedirectFactory()
        obj.new_site = factories.SiteFactory()
        obj.save()
        self.response.status_code = 404
        self.request.scheme = "https"
        self.request.path = "/the-old-path/"
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(
            response.url, "https://%s%s" % (obj.new_site.domain, obj.new_path))

    def test_wildcard_redirect(self):
        obj = factories.RedirectFactory()
        obj.old_path = "/the-wildcard/yes/"
        obj.wildcard_match = True
        obj.save()
        self.response.status_code = 404
        self.request.path = "%sthe/right/part/" % obj.old_path
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "/the-new-path/")

    def test_wildcard_redirect_keep_tree(self):
        obj = factories.RedirectFactory()
        obj.old_path = "/the-wildcard/yes/"
        obj.wildcard_match = True
        obj.keep_tree = True
        obj.save()
        self.response.status_code = 404
        self.request.path = "%sthe/right/part/" % obj.old_path
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "/the-new-path/the/right/part/")

    def test_wildcard_redirect_with_site(self):
        obj = factories.RedirectFactory()
        obj.site = Site.objects.get_current()
        obj.old_path = "/the-wildcard/yes/"
        obj.wildcard_match = True
        obj.save()
        self.response.status_code = 404
        self.request.path = "%sthe/right/part/" % obj.old_path
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "/the-new-path/")

    def test_redirect_without_slash(self):
        obj = factories.RedirectFactory()
        obj.old_path = '/whatever/check.html'
        obj.save()
        self.request.path = obj.old_path
        self.response.status_code = 404
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "/the-new-path/")

    def test_from_custom_domain(self):
        obj = factories.RedirectFactory()
        obj.domain = 'custom.com'
        obj.old_path = '/'
        obj.new_path = 'http://another.com/'
        obj.save()
        self.request.path = obj.old_path
        self.request.get_host = lambda: 'custom.com'
        self.response.status_code = 200
        response = self.middleware.process_request(self.request, )
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "http://another.com/")

    def test_from_custom_domain_false_positive(self):
        obj = factories.RedirectFactory()
        obj.domain = 'custom.com'
        obj.old_path = '/'
        obj.new_path = 'http://another.com/'
        obj.save()
        self.request.path = obj.old_path
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
        self.request.path = very_long
        # check for false positives!
        self.response.status_code = 404
        response = self.middleware.process_response(self.request, self.response)
        self.assertEqual(404, response.status_code)
        self.assertEqual(1, Redirect.objects.all().count())
        self.assertEqual(conf.INDEXED_CHARFIELD_MAX_LENGTH, len(Redirect.objects.all()[0].old_path))
