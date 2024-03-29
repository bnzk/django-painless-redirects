import django
from django.contrib.auth.models import User
from django.test import TestCase, Client

# compat thing!
from painless_redirects.models import Redirect

if django.VERSION[:2] < (1, 10):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse


class PainlessAdminTests(TestCase):

    USER = 'fred'
    PASSWORD = 'tst'

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(
            username=self.USER,
            password=self.PASSWORD,
            email='test@test.fred',
        )

    def tearDown(self):
        pass

    def test_basic_admin_change_view(self):
        self.client.login(username=self.USER, password=self.PASSWORD)
        obj = Redirect.objects.create(
            old_path="/the-old-path/",
            new_path="/the-new-path/",
        )
        url = reverse('admin:painless_redirects_redirect_changelist')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        url = reverse('admin:painless_redirects_redirect_change', args=(obj.id, ))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_admin_action_ignore(self):
        self.client.login(username=self.USER, password=self.PASSWORD)
        obj = Redirect.objects.create(
            old_path="/the-old-path/",
            new_path="/the-new-path/",
        )
        url = reverse('admin:painless_redirects_redirect_changelist')
        data = {
            # csrfmiddlewaretoken: xXBOESWn3YbibfJLW1Q1i348dUe0WDlYCf5JsXVoxbRkfGTJ9fkaHCG5dbDmNu9T
            'action': 'set_ignored',
            'select_across': 0,
            'index': 0,
            '_selected_action': obj.id,
        }
        response = self.client.post(url, data, follow=False)
        self.assertLess(response.status_code, 400)
        obj = Redirect.objects.get(pk=obj.id)
        self.assertTrue(obj.ignored)
