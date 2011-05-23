from django.forms import ValidationError
from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured
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


class MultiFormViewTests(TestCase):
    urls = 'extra_views.tests.urls'
    
    valid_order = {
        'order-form_id': None,
        'order-name': 'Joe Bloggs'
    }
    valid_address = {
        'address-form_id': None,
        'address-name': 'Joe Bloggs',
        'address-city': u'',
        'address-line1': u'',
        'address-line2': u'',
        'address-postcode': u'ABC 123',
    }
    invalid_order = {
        'order-form_id': None,                     
    }    
    invalid_address = {
        'address-form_id': None,
    }
    
    def test_create(self):
        res = self.client.get('/multiview/simple/')
        self.assertEqual(res.status_code, 200)
        self.assertTrue('order_form' in res.context)
        self.assertTrue('address_form' in res.context)
        self.assertEquals(res.context['order_form'].__class__.__name__, 'OrderForm')
        self.assertEquals(res.context['address_form'].__class__.__name__, 'AddressForm')
        self.assertTrue('form_id' in res.context['order_form'].fields)
        self.assertTrue('form_id' in res.context['address_form'].fields)
        
    def test_nosuccess(self):
        with self.assertRaises(ImproperlyConfigured):
            self.client.post('/multiview/nosuccess/', {}, follow=True)        
        
    def test_empty_success(self):
        res = self.client.post('/multiview/simple/', {}, follow=True)
        self.assertRedirects(res, '/multiview/simple/valid/', status_code=302)
        
    def test_order_success(self):
        data = {}
        data.update(self.valid_order)
        res = self.client.post('/multiview/simple/', data, follow=True)
        
        self.assertRedirects(res, '/multiview/simple/valid/', status_code=302)
        
    def test_both_success(self):
        data = {}
        data.update(self.valid_order)
        data.update(self.valid_address)
        
        res = self.client.post('/multiview/simple/', data, follow=True)
        self.assertRedirects(res, '/multiview/simple/valid/', status_code=302)
        
    def test_order_invalid(self):
        data = {}
        data.update(self.invalid_order)
        data.update(self.valid_address)
        
        res = self.client.post('/multiview/simple/', data, follow=True)
        self.assertEquals(res.status_code, 200)
        self.assertEquals(len(res.context['order_form'].errors), 1)
        self.assertEquals(len(res.context['address_form'].errors), 0)

    def test_address_invalid(self):
        data = {}
        data.update(self.valid_order)
        data.update(self.invalid_address)
        
        res = self.client.post('/multiview/simple/', data, follow=True)
        self.assertEquals(res.status_code, 200)
        self.assertEquals(len(res.context['order_form'].errors), 0)
        self.assertEquals(len(res.context['address_form'].errors), 2)
        
    def test_both_invalid(self):
        data = {}
        data.update(self.invalid_order)
        data.update(self.invalid_address)
        
        res = self.client.post('/multiview/simple/', data, follow=True)
        self.assertEquals(res.status_code, 200)
        self.assertEquals(len(res.context['order_form'].errors), 1)
        self.assertEquals(len(res.context['address_form'].errors), 2)
        
    def test_valid_handler(self):
        data = {}
        data.update(self.valid_order)
        
        res = self.client.post('/multiview/handlers/', data, follow=True)
        self.assertEquals(res.status_code, 200)
        self.assertEquals(self.client.session['valid_order'], 'Joe Bloggs')
        self.assertEquals(self.client.session['forms_valid'], 'All')

    def test_invalid_handler(self):
        data = {}
        data.update(self.invalid_address)
        
        res = self.client.post('/multiview/handlers/', data, follow=True)
        self.assertEquals(res.status_code, 200)
        self.assertEquals(self.client.session['invalid_address'], 'Error')
        self.assertEquals(self.client.session['forms_invalid'], 'Any')        

    def test_initial_data(self):
        res = self.client.get('/multiview/initialdata/')
        self.assertEquals(res.status_code, 200)
        self.assertEquals(res.context['order_form']['name'].value(), 'Sally Jones')
        self.assertEquals(res.context['address_form']['name'].value(), 'Sally Jones')
        self.assertEquals(res.context['address_form']['postcode'].value(), 'ABC 123')
 
    def test_initial_handlers(self):
        res = self.client.get('/multiview/initialhandler/')
        self.assertEquals(res.status_code, 200)
        self.assertEquals(res.context['order_form']['name'].value(), 'Bob Jones')
        self.assertEquals(res.context['address_form']['name'].value(), 'Bob Jones')
        self.assertEquals(res.context['address_form']['postcode'].value(), 'XYZ 789') 
