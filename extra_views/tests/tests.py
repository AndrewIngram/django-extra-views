from django.test import TestCase
from django.forms import ValidationError
from django.utils.unittest import expectedFailure

class FormsetViewTests(TestCase):
    urls = 'extra_views.tests.urls'
    management_data = {
            'form-TOTAL_FORMS': u'2',
            'form-INITIAL_FORMS': u'0',
            'form-MAX_NUM_FORMS': u'',
        }
    
    def test_create(self):
        res = self.client.get('/formset/simple/')
        self.assertEqual(res.status_code, 200)
        self.assertTrue('formset' in res.context)
        self.assertFalse('form' in res.context)
        self.assertTemplateUsed(res, 'extra_views/address_formset.html')
        self.assertEquals(res.context['formset'].__class__.__name__, 'AddressFormFormSet')
        
    def test_missing_management(self):
        with self.assertRaises(ValidationError):
            self.client.post('/formset/simple/', {})            
        
    def test_success(self):            
        res = self.client.post('/formset/simple/', self.management_data, follow=True)
        self.assertRedirects(res, '/formset/simple/', status_code=302)
        
    @expectedFailure        
    def test_put(self):
        res = self.client.put('/formset/simple/', self.management_data, follow=True)
        self.assertRedirects(res, '/formset/simple/', status_code=302)        

    def test_success_url(self):            
        res = self.client.post('/formset/simple_redirect/', self.management_data, follow=True)
        self.assertRedirects(res, '/formset/simple_redirect/valid/')

    def test_invalid(self):
        data = {
            'form-0-name': u'Joe Bloggs',
            'form-0-city': u'',
            'form-0-line1': u'',
            'form-0-line2': u'',
            'form-0-postcode': u'',
        }
        data.update(self.management_data)
        
        res = self.client.post('/formset/simple/', data, follow=True)        
        self.assertEquals(res.status_code, 200)
        self.assertTrue('postcode' in res.context['formset'].errors[0])
        
    def test_formset_class(self):
        res = self.client.get('/formset/custom/')
        self.assertEqual(res.status_code, 200)
        
       
class ModelFormsetViewTests(TestCase):
    urls = 'extra_views.tests.urls'
    management_data = {
            'form-TOTAL_FORMS': u'2',
            'form-INITIAL_FORMS': u'0',
            'form-MAX_NUM_FORMS': u'',
        }
    
    def test_create(self):
        res = self.client.get('/modelformset/simple/')        
        self.assertEqual(res.status_code, 200)
        self.assertTrue('formset' in res.context)
        self.assertFalse('form' in res.context)
        self.assertTemplateUsed(res, 'extra_views/item_formset.html')
        self.assertEquals(res.context['formset'].__class__.__name__, 'ItemFormFormSet')
        
    
        
        
