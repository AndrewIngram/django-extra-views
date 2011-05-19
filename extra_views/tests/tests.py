from django.test import TestCase

class FormsetTests(TestCase):
    urls = 'extra_views.tests.urls'
    
    def test_one(self):
        res = self.client.get('/formset/simple/')
        self.assertEqual(res.status_code, 200)
        
        print res 
