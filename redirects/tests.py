from django.test import TestCase, Client
from .models import PathMatchRedirect

# Create your tests here.
class RedirectsCase(TestCase):


    def test_no_redirect(self):
        c = Client()
        response = c.get('/en/test/') # Needs the /en/ otherwise it tried to redirect to it
        self.assertEquals(404, response.status_code)
        
    def test_basic_redirect(self):
        PathMatchRedirect.objects.create(match="/test/", replace="/replaced/", preserve_extra=False)
        c = Client()
        response = c.get('/test/')
        self.assertEquals(301, response.status_code)
        self.assertEquals('http://testserver/replaced/', response['Location'])
        
    def test_redirect_precedence(self):
        PathMatchRedirect.objects.create(match="/test/", replace="/replaced/", preserve_extra=False)
        PathMatchRedirect.objects.create(match="/test/specific/", replace="/specific/", preserve_extra=False)
        PathMatchRedirect.objects.create(match="/test/spec", replace="/premature_match/", preserve_extra=False)
        c = Client()
        response = c.get('/test/specific/')
        self.assertEquals(301, response.status_code)
        self.assertEquals('http://testserver/specific/', response['Location'])

    def test_redirect_preserve_extra(self):
        PathMatchRedirect.objects.create(match="/test/", replace="/replaced/", preserve_extra=True)
        c = Client()
        response = c.get('/test/extra/path')
        self.assertEquals(301, response.status_code)
        self.assertEquals('http://testserver/replaced/extra/path', response['Location'])
