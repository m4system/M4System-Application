from django.test import TestCase
from djcelery.models import PeriodicTask

from scheduler.models import HostChecks


class WebviewLoginPageTest(TestCase):
    fixtures = ['djcelery.json', 'user.json', 'auth.json', 'scheduler.json', 'webview.json']

    def test_loading_login_page(self):
        """
        Do a get to / and confirm that the response code is 302 to /login/?next=/
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/?next=/')

    def test_login_in(self):
        """
        Perform an actual login to confirm it works
        """
        isLogin = self.client.login(username='m4', password='Changeme1!')
        self.assertEqual(isLogin, True)

    def test_update_hostcheck(self):
        """
        Update a check and confirm all sub objects are updated.
        """
        check = HostChecks.objects.get(name='Test1')
        check.interval = "30"
        check.save()
        task = PeriodicTask.objects.get(name='Localhost-Test1')
        self.assertEqual(task.interval.every, 30)
        check.interval = "10"
        check.save()
        task = PeriodicTask.objects.get(name='Localhost-Test1')
        self.assertEqual(task.interval.every, 10)
