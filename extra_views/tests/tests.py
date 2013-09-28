import datetime
from decimal import Decimal as D

from django.core.exceptions import ImproperlyConfigured
from django.forms import ValidationError
from django.test import TransactionTestCase
from django.utils.unittest import expectedFailure

from .models import Item, Order, Tag, Event


class FormSetViewTests(TransactionTestCase):
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

    def test_formset_named(self):
        res = self.client.get('/formset/simple/named/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['formset'], res.context['AddressFormset'])

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


class ModelFormSetViewTests(TransactionTestCase):
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

    def test_override(self):
        res = self.client.get('/modelformset/custom/')
        self.assertEqual(res.status_code, 200)
        form = res.context['formset'].forms[0]
        self.assertEquals(form['flag'].value(), True)
        self.assertEquals(form['notes'].value(), 'Write notes here')

    def test_post(self):
        order = Order(name='Dummy Order')
        order.save()

        data = {
            'form-0-name': 'Bubble Bath',
            'form-0-sku': '1234567890123',
            'form-0-price': D('9.99'),
            'form-0-order': order.id,
            'form-0-status': 0,
        }
        data.update(self.management_data)
        data['form-TOTAL_FORMS'] = u'1'
        res = self.client.post('/modelformset/simple/', data, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEquals(Item.objects.all().count(), 1)

    def test_context(self):
        order = Order(name='Dummy Order')
        order.save()

        for i in range(10):
            item = Item(name='Item %i' % i, sku=str(i) * 13, price=D('9.99'), order=order, status=0)
            item.save()

        res = self.client.get('/modelformset/simple/')
        self.assertTrue('object_list' in res.context)
        self.assertEquals(len(res.context['object_list']), 10)


class InlineFormSetViewTests(TransactionTestCase):
    urls = 'extra_views.tests.urls'
    management_data = {
        'items-TOTAL_FORMS': u'2',
        'items-INITIAL_FORMS': u'0',
        'items-MAX_NUM_FORMS': u'',
    }

    def test_create(self):
        order = Order(name='Dummy Order')
        order.save()

        for i in range(10):
            item = Item(name='Item %i' % i, sku=str(i) * 13, price=D('9.99'), order=order, status=0)
            item.save()

        res = self.client.get('/inlineformset/1/')

        self.assertTrue('object' in res.context)
        self.assertTrue('order' in res.context)

        self.assertEqual(res.status_code, 200)
        self.assertTrue('formset' in res.context)
        self.assertFalse('form' in res.context)

    def test_post(self):
        order = Order(name='Dummy Order')
        order.save()
        data = {}
        data.update(self.management_data)

        res = self.client.post('/inlineformset/1/', data, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue('formset' in res.context)
        self.assertFalse('form' in res.context)

    def test_save(self):
        order = Order(name='Dummy Order')
        order.save()
        data = {
            'items-0-name': 'Bubble Bath',
            'items-0-sku': '1234567890123',
            'items-0-price': D('9.99'),
            'items-0-order': order.id,
            'items-0-status': 0,
            'items-1-DELETE': True,
        }
        data.update(self.management_data)

        self.assertEquals(0, order.items.count())
        res = self.client.post('/inlineformset/1/', data, follow=True)
        order = Order.objects.get(id=1)

        context_instance = res.context['formset'][0].instance

        self.assertEquals('Bubble Bath', context_instance.name)
        self.assertEquals('', res.context['formset'][1].instance.name)

        self.assertEquals(1, order.items.count())


class GenericInlineFormSetViewTests(TransactionTestCase):
    urls = 'extra_views.tests.urls'

    def test_get(self):
        order = Order(name='Dummy Order')
        order.save()

        order2 = Order(name='Other Order')
        order2.save()

        tag = Tag(name='Test', content_object=order)
        tag.save()

        tag = Tag(name='Test2', content_object=order2)
        tag.save()

        res = self.client.get('/genericinlineformset/1/')

        self.assertEqual(res.status_code, 200)
        self.assertTrue('formset' in res.context)
        self.assertFalse('form' in res.context)
        self.assertEquals('Test', res.context['formset'].forms[0]['name'].value())

    def test_post(self):
        order = Order(name='Dummy Order')
        order.save()

        tag = Tag(name='Test', content_object=order)
        tag.save()

        data = {
            'tests-tag-content_type-object_id-TOTAL_FORMS': 3,
            'tests-tag-content_type-object_id-INITIAL_FORMS': 1,
            'tests-tag-content_type-object_id-MAX_NUM_FORMS': u'',
            'tests-tag-content_type-object_id-0-name': 'Updated',
            'tests-tag-content_type-object_id-0-id': 1,
            'tests-tag-content_type-object_id-1-DELETE': True,
            'tests-tag-content_type-object_id-2-DELETE': True,
        }

        res = self.client.post('/genericinlineformset/1/', data, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEquals('Updated', res.context['formset'].forms[0]['name'].value())
        self.assertEquals(1, Tag.objects.count())

    def test_post2(self):
        order = Order(name='Dummy Order')
        order.save()

        tag = Tag(name='Test', content_object=order)
        tag.save()

        data = {
            'tests-tag-content_type-object_id-TOTAL_FORMS': 3,
            'tests-tag-content_type-object_id-INITIAL_FORMS': 1,
            'tests-tag-content_type-object_id-MAX_NUM_FORMS': u'',
            'tests-tag-content_type-object_id-0-name': 'Updated',
            'tests-tag-content_type-object_id-0-id': 1,
            'tests-tag-content_type-object_id-1-name': 'Tag 2',
            'tests-tag-content_type-object_id-2-name': 'Tag 3',
        }

        res = self.client.post('/genericinlineformset/1/', data, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEquals(3, Tag.objects.count())


class ModelWithInlinesTests(TransactionTestCase):
    urls = 'extra_views.tests.urls'

    def test_create(self):
        res = self.client.get('/inlines/new/')
        self.assertEqual(res.status_code, 200)
        self.assertEquals(0, Tag.objects.count())

        data = {
            'name': u'Dummy Order',
            'items-TOTAL_FORMS': u'2',
            'items-INITIAL_FORMS': u'0',
            'items-MAX_NUM_FORMS': u'',
            'items-0-name': 'Bubble Bath',
            'items-0-sku': '1234567890123',
            'items-0-price': D('9.99'),
            'items-0-status': 0,
            'items-0-order': u'',
            'items-1-DELETE': True,
            'tests-tag-content_type-object_id-TOTAL_FORMS': 2,
            'tests-tag-content_type-object_id-INITIAL_FORMS': 0,
            'tests-tag-content_type-object_id-MAX_NUM_FORMS': u'',
            'tests-tag-content_type-object_id-0-name': u'Test',
            'tests-tag-content_type-object_id-1-DELETE': True,
        }

        res = self.client.post('/inlines/new/', data, follow=True)

        self.assertTrue('object' in res.context)
        self.assertTrue('order' in res.context)

        self.assertEqual(res.status_code, 200)
        self.assertEquals(1, Tag.objects.count())

    def test_named_create(self):
        res = self.client.get('/inlines/new/named/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['Items'], res.context['inlines'][0])
        self.assertEqual(res.context['Tags'], res.context['inlines'][1])

    def test_validation(self):
        data = {
            'items-TOTAL_FORMS': u'2',
            'items-INITIAL_FORMS': u'0',
            'items-MAX_NUM_FORMS': u'',
            'items-0-name': 'Test Item 1',
            'items-0-sku': '',
            'items-0-price': '',
            'items-0-status': 0,
            'items-0-order': '',
            'items-1-name': '',
            'items-1-sku': '',
            'items-1-price': '',
            'items-1-status': '',
            'items-1-order': '',
            'items-1-DELETE': True,
            'tests-tag-content_type-object_id-TOTAL_FORMS': 2,
            'tests-tag-content_type-object_id-INITIAL_FORMS': 0,
            'tests-tag-content_type-object_id-MAX_NUM_FORMS': u'',
            'tests-tag-content_type-object_id-0-name': u'Test',
            'tests-tag-content_type-object_id-1-DELETE': True,
        }

        res = self.client.post('/inlines/new/', data, follow=True)
        self.assertEquals(len(res.context['form'].errors), 1)
        self.assertEquals(len(res.context['inlines'][0].errors[0]), 2)

    def test_update(self):
        order = Order(name='Dummy Order')
        order.save()

        for i in range(2):
            item = Item(name='Item %i' % i, sku=str(i) * 13, price=D('9.99'), order=order, status=0)
            item.save()

        tag = Tag(name='Test', content_object=order)
        tag.save()

        res = self.client.get('/inlines/1/')

        self.assertEqual(res.status_code, 200)
        order = Order.objects.get(id=1)

        self.assertEquals(2, order.items.count())
        self.assertEquals('Item 0', order.items.all()[0].name)

        data = {
            'name': u'Dummy Order',
            'items-TOTAL_FORMS': u'4',
            'items-INITIAL_FORMS': u'2',
            'items-MAX_NUM_FORMS': u'',
            'items-0-name': 'Bubble Bath',
            'items-0-sku': '1234567890123',
            'items-0-price': D('9.99'),
            'items-0-status': 0,
            'items-0-order': 1,
            'items-0-id': 1,
            'items-1-name': 'Bubble Bath',
            'items-1-sku': '1234567890123',
            'items-1-price': D('9.99'),
            'items-1-status': 0,
            'items-1-order': 1,
            'items-1-id': 2,
            'items-2-name': 'Bubble Bath',
            'items-2-sku': '1234567890123',
            'items-2-price': D('9.99'),
            'items-2-status': 0,
            'items-2-order': 1,
            'items-3-DELETE': True,
            'tests-tag-content_type-object_id-TOTAL_FORMS': 3,
            'tests-tag-content_type-object_id-INITIAL_FORMS': 1,
            'tests-tag-content_type-object_id-MAX_NUM_FORMS': u'',
            'tests-tag-content_type-object_id-0-name': u'Test',
            'tests-tag-content_type-object_id-0-id': 1,
            'tests-tag-content_type-object_id-0-DELETE': True,
            'tests-tag-content_type-object_id-1-name': u'Test 2',
            'tests-tag-content_type-object_id-2-name': u'Test 3',
        }

        res = self.client.post('/inlines/1/', data, follow=True)
        self.assertEqual(res.status_code, 200)

        order = Order.objects.get(id=1)

        self.assertEquals(3, order.items.count())
        self.assertEquals(2, Tag.objects.count())
        self.assertEquals('Bubble Bath', order.items.all()[0].name)

    def test_parent_instance_saved_in_form_save(self):
        order = Order(name='Dummy Order')
        order.save()

        data = {
            'name': u'Dummy Order',
            'items-TOTAL_FORMS': u'0',
            'items-INITIAL_FORMS': u'0',
            'items-MAX_NUM_FORMS': u'',
            'tests-tag-content_type-object_id-TOTAL_FORMS': u'0',
            'tests-tag-content_type-object_id-INITIAL_FORMS': u'0',
            'tests-tag-content_type-object_id-MAX_NUM_FORMS': u'',
        }

        res = self.client.post('/inlines/1/', data, follow=True)
        self.assertEqual(res.status_code, 200)

        order = Order.objects.get(id=1)
        self.assertTrue(order.action_on_save)
