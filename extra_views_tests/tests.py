import datetime
from decimal import Decimal as D
from unittest import expectedFailure

import django
from django.contrib.messages import get_messages
from django.core.exceptions import ImproperlyConfigured
from django.forms import ValidationError
from django.test import TestCase

from .models import Event, Item, Order, Tag


class FormSetViewTests(TestCase):
    management_data = {
        "form-TOTAL_FORMS": "2",
        "form-INITIAL_FORMS": "0",
        "form-MAX_NUM_FORMS": "",
    }

    def test_create(self):
        res = self.client.get("/formset/simple/")
        self.assertEqual(res.status_code, 200)
        self.assertTrue("formset" in res.context)
        self.assertFalse("form" in res.context)
        self.assertTemplateUsed(res, "extra_views/address_formset.html")
        self.assertEqual(
            res.context["formset"].__class__.__name__, "AddressFormFormSet"
        )

    def test_formset_named(self):
        res = self.client.get("/formset/simple/named/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context["formset"], res.context["AddressFormset"])

    def test_missing_management_form(self):
        # Django >=3.2 and does not raise an exception, but returns an error.
        if django.__version__ >= "3.2.0":
            res = self.client.post("/formset/simple/", {})
            self.assertEqual(200, res.status_code)
            formset = res.context["formset"]
            self.assertFalse(formset.is_valid())
            self.assertIn(
                "ManagementForm data is missing or has been tampered with",
                formset.non_form_errors()[0],
            )
        else:
            with self.assertRaisesRegex(
                ValidationError,
                "ManagementForm data is missing or has been tampered with",
            ):
                self.client.post("/formset/simple/", {})

    def test_success(self):
        res = self.client.post("/formset/simple/", self.management_data, follow=True)
        self.assertRedirects(res, "/formset/simple/", status_code=302)

    def test_success_message(self):
        res = self.client.post("/formset/simple/", self.management_data, follow=True)
        messages = [
            message.__str__() for message in get_messages(res.context["view"].request)
        ]
        self.assertIn("Formset objects were created successfully!", messages)

    @expectedFailure
    def test_put(self):
        res = self.client.put("/formset/simple/", self.management_data, follow=True)
        self.assertRedirects(res, "/formset/simple/", status_code=302)

    def test_success_url(self):
        res = self.client.post(
            "/formset/simple_redirect/", self.management_data, follow=True
        )
        self.assertRedirects(res, "/formset/simple_redirect/valid/")

    def test_invalid(self):
        data = {
            "form-0-name": "Joe Bloggs",
            "form-0-city": "",
            "form-0-line1": "",
            "form-0-line2": "",
            "form-0-postcode": "",
        }
        data.update(self.management_data)

        res = self.client.post("/formset/simple/", data, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue("postcode" in res.context["formset"].errors[0])

    def test_formset_class(self):
        res = self.client.get("/formset/custom/")
        self.assertEqual(res.status_code, 200)

    def test_inital(self):
        res = self.client.get("/formset/simple/kwargs/")
        self.assertEqual(res.status_code, 200)
        initial_forms = res.context["formset"].initial_forms
        self.assertTrue(initial_forms)
        self.assertEqual(initial_forms[0].initial, {"name": "address1"})

    def test_prefix(self):
        res = self.client.get("/formset/simple/kwargs/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context["formset"].management_form.prefix, "test_prefix")

    def test_factory_kwargs(self):
        res = self.client.get("/formset/simple/kwargs/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.context["formset"].management_form.initial["MAX_NUM_FORMS"], 27
        )

    def test_formset_kwargs(self):
        res = self.client.get("/formset/simple/kwargs/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context["formset"].management_form.auto_id, "id_test_%s")
        initial_forms = res.context["formset"].initial_forms
        self.assertTrue(initial_forms)
        self.assertTrue(initial_forms[0].empty_permitted)


class ModelFormSetViewTests(TestCase):
    management_data = {
        "form-TOTAL_FORMS": "2",
        "form-INITIAL_FORMS": "0",
        "form-MAX_NUM_FORMS": "",
    }

    def test_create(self):
        res = self.client.get("/modelformset/simple/")
        self.assertEqual(res.status_code, 200)
        self.assertTrue("formset" in res.context)
        self.assertFalse("form" in res.context)
        self.assertTemplateUsed(res, "extra_views/item_formset.html")
        self.assertEqual(res.context["formset"].__class__.__name__, "ItemFormFormSet")

    def test_override(self):
        res = self.client.get("/modelformset/custom/")
        self.assertEqual(res.status_code, 200)
        form = res.context["formset"].forms[0]
        self.assertEqual(form["flag"].value(), True)
        self.assertEqual(form["notes"].value(), "Write notes here")

    def test_post(self):
        order = Order(name="Dummy Order")
        order.save()

        data = {
            "form-0-name": "Bubble Bath",
            "form-0-sku": "1234567890123",
            "form-0-price": D("9.99"),
            "form-0-order": order.id,
            "form-0-status": 0,
        }
        data.update(self.management_data)
        data["form-TOTAL_FORMS"] = "1"
        res = self.client.post("/modelformset/simple/", data, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Item.objects.all().count(), 1)

    def test_context(self):
        order = Order(name="Dummy Order")
        order.save()

        for i in range(10):
            item = Item(
                name="Item %i" % i,
                sku=str(i) * 13,
                price=D("9.99"),
                order=order,
                status=0,
            )
            item.save()

        res = self.client.get("/modelformset/simple/")
        self.assertTrue("object_list" in res.context)
        self.assertEqual(len(res.context["object_list"]), 10)

    def test_fields_is_used(self):
        res = self.client.get("/modelformset/simple/")
        self.assertEqual(res.status_code, 200)
        fields = res.context["formset"].empty_form.fields
        self.assertIn("sku", fields)
        self.assertNotIn("date_placed", fields)

    def test_exclude_is_used(self):
        res = self.client.get("/modelformset/exclude/")
        self.assertEqual(res.status_code, 200)
        fields = res.context["formset"].empty_form.fields
        self.assertIn("date_placed", fields)
        self.assertNotIn("sku", fields)


class InlineFormSetViewTests(TestCase):
    management_data = {
        "items-TOTAL_FORMS": "2",
        "items-INITIAL_FORMS": "0",
        "items-MAX_NUM_FORMS": "",
    }

    def test_create(self):
        order = Order(name="Dummy Order")
        order.save()

        for i in range(10):
            item = Item(
                name="Item %i" % i,
                sku=str(i) * 13,
                price=D("9.99"),
                order=order,
                status=0,
            )
            item.save()

        res = self.client.get("/inlineformset/{}/".format(order.id))

        self.assertTrue("object" in res.context)
        self.assertTrue("order" in res.context)

        self.assertEqual(res.status_code, 200)
        self.assertTrue("formset" in res.context)
        self.assertFalse("form" in res.context)

    def test_post(self):
        order = Order(name="Dummy Order")
        order.save()
        data = {}
        data.update(self.management_data)

        res = self.client.post("/inlineformset/{}/".format(order.id), data, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue("formset" in res.context)
        self.assertFalse("form" in res.context)

    def test_save(self):
        order = Order(name="Dummy Order")
        order.save()
        data = {
            "items-0-name": "Bubble Bath",
            "items-0-sku": "1234567890123",
            "items-0-price": D("9.99"),
            "items-0-status": 0,
            "items-1-DELETE": True,
        }
        data.update(self.management_data)

        self.assertEqual(0, order.items.count())
        res = self.client.post("/inlineformset/{}/".format(order.id), data, follow=True)
        order = Order.objects.get(id=order.id)

        context_instance = res.context["formset"][0].instance

        self.assertEqual("Bubble Bath", context_instance.name)
        self.assertEqual("", res.context["formset"][1].instance.name)

        self.assertEqual(1, order.items.count())


class GenericInlineFormSetViewTests(TestCase):
    def test_get(self):
        order = Order(name="Dummy Order")
        order.save()

        order2 = Order(name="Other Order")
        order2.save()

        tag = Tag(name="Test", content_object=order)
        tag.save()

        tag = Tag(name="Test2", content_object=order2)
        tag.save()

        res = self.client.get("/genericinlineformset/{}/".format(order.id))

        self.assertEqual(res.status_code, 200)
        self.assertTrue("formset" in res.context)
        self.assertFalse("form" in res.context)
        self.assertEqual("Test", res.context["formset"].forms[0]["name"].value())

    def test_post(self):
        order = Order(name="Dummy Order")
        order.save()

        tag = Tag(name="Test", content_object=order)
        tag.save()

        data = {
            "extra_views_tests-tag-content_type-object_id-TOTAL_FORMS": 3,
            "extra_views_tests-tag-content_type-object_id-INITIAL_FORMS": 1,
            "extra_views_tests-tag-content_type-object_id-MAX_NUM_FORMS": "",
            "extra_views_tests-tag-content_type-object_id-0-name": "Updated",
            "extra_views_tests-tag-content_type-object_id-0-id": 1,
            "extra_views_tests-tag-content_type-object_id-1-DELETE": True,
            "extra_views_tests-tag-content_type-object_id-2-DELETE": True,
        }

        res = self.client.post(
            "/genericinlineformset/{}/".format(order.id), data, follow=True
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual("Updated", res.context["formset"].forms[0]["name"].value())
        self.assertEqual(1, Tag.objects.count())

    def test_post2(self):
        order = Order(name="Dummy Order")
        order.save()

        tag = Tag(name="Test", content_object=order)
        tag.save()

        data = {
            "extra_views_tests-tag-content_type-object_id-TOTAL_FORMS": 3,
            "extra_views_tests-tag-content_type-object_id-INITIAL_FORMS": 1,
            "extra_views_tests-tag-content_type-object_id-MAX_NUM_FORMS": "",
            "extra_views_tests-tag-content_type-object_id-0-name": "Updated",
            "extra_views_tests-tag-content_type-object_id-0-id": tag.id,
            "extra_views_tests-tag-content_type-object_id-1-name": "Tag 2",
            "extra_views_tests-tag-content_type-object_id-2-name": "Tag 3",
        }

        res = self.client.post(
            "/genericinlineformset/{}/".format(order.id), data, follow=True
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(3, Tag.objects.count())

    def test_intial_data_is_used(self):
        # Specific test for initial data in genericinlineformset
        order = Order(name="Dummy Order")
        order.save()
        res = self.client.get("/genericinlineformset/{}/".format(order.id))
        self.assertEqual(res.status_code, 200)
        extra_forms = res.context["formset"].extra_forms
        self.assertTrue(extra_forms)
        self.assertEqual(extra_forms[0].initial, {"name": "test_tag_name"})


class ModelWithInlinesTests(TestCase):
    def test_create(self):
        res = self.client.get("/inlines/new/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(0, Tag.objects.count())

        data = {
            "name": "Dummy Order",
            "items-TOTAL_FORMS": "2",
            "items-INITIAL_FORMS": "0",
            "items-MAX_NUM_FORMS": "",
            "items-0-name": "Bubble Bath",
            "items-0-sku": "1234567890123",
            "items-0-price": D("9.99"),
            "items-0-status": 0,
            "items-1-DELETE": True,
            "extra_views_tests-tag-content_type-object_id-TOTAL_FORMS": 2,
            "extra_views_tests-tag-content_type-object_id-INITIAL_FORMS": 0,
            "extra_views_tests-tag-content_type-object_id-MAX_NUM_FORMS": "",
            "extra_views_tests-tag-content_type-object_id-0-name": "Test",
            "extra_views_tests-tag-content_type-object_id-1-DELETE": True,
        }

        res = self.client.post("/inlines/new/", data, follow=True)

        self.assertTrue("object" in res.context)
        self.assertTrue("order" in res.context)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(1, Tag.objects.count())

        # Check that form_valid has been called.
        self.assertRedirects(res, "/inlines/1/?form_valid_called=1")

    def test_create_success_message(self):
        res = self.client.get("/inlines/new/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(0, Tag.objects.count())

        data = {
            "name": "Dummy Order",
            "items-TOTAL_FORMS": "2",
            "items-INITIAL_FORMS": "0",
            "items-MAX_NUM_FORMS": "",
            "items-0-name": "Bubble Bath",
            "items-0-sku": "1234567890123",
            "items-0-price": D("9.99"),
            "items-0-status": 0,
            "items-1-DELETE": True,
            "extra_views_tests-tag-content_type-object_id-TOTAL_FORMS": 2,
            "extra_views_tests-tag-content_type-object_id-INITIAL_FORMS": 0,
            "extra_views_tests-tag-content_type-object_id-MAX_NUM_FORMS": "",
            "extra_views_tests-tag-content_type-object_id-0-name": "Test",
            "extra_views_tests-tag-content_type-object_id-1-DELETE": True,
        }

        res = self.client.post("/inlines/new/", data, follow=True)

        messages = [
            message.__str__() for message in get_messages(res.context["view"].request)
        ]
        self.assertIn("Order Dummy Order was created successfully!", messages)

    def test_named_create(self):
        res = self.client.get("/inlines/new/named/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context["Items"], res.context["inlines"][0])
        self.assertEqual(res.context["Tags"], res.context["inlines"][1])

    def test_validation(self):
        data = {
            "items-TOTAL_FORMS": "2",
            "items-INITIAL_FORMS": "0",
            "items-MAX_NUM_FORMS": "",
            "items-0-name": "Test Item 1",
            "items-0-sku": "",
            "items-0-price": "",
            "items-0-status": 0,
            "items-1-name": "",
            "items-1-sku": "",
            "items-1-price": "",
            "items-1-status": "",
            "items-1-DELETE": True,
            "extra_views_tests-tag-content_type-object_id-TOTAL_FORMS": 2,
            "extra_views_tests-tag-content_type-object_id-INITIAL_FORMS": 0,
            "extra_views_tests-tag-content_type-object_id-MAX_NUM_FORMS": "",
            "extra_views_tests-tag-content_type-object_id-0-name": "Test",
            "extra_views_tests-tag-content_type-object_id-1-DELETE": True,
        }

        res = self.client.post("/inlines/new/", data, follow=True)
        self.assertEqual(len(res.context["form"].errors), 1)
        self.assertEqual(len(res.context["inlines"][0].errors[0]), 2)

    def test_view_object_is_none_after_failed_validation_for_createview(self):
        # We are testing that view.object = None even if the form validates
        # but one of the inline formsets does not.
        data = {
            "name": "Dummy Order",
            "items-TOTAL_FORMS": "2",
            "items-INITIAL_FORMS": "0",
            "items-MAX_NUM_FORMS": "",
            "items-0-name": "Test Item 1",
            "items-0-sku": "",
            "items-0-price": "",
            "items-0-status": 0,
            "items-1-name": "",
            "items-1-sku": "",
            "items-1-price": "",
            "items-1-status": "",
            "items-1-DELETE": True,
            "extra_views_tests-tag-content_type-object_id-TOTAL_FORMS": 2,
            "extra_views_tests-tag-content_type-object_id-INITIAL_FORMS": 0,
            "extra_views_tests-tag-content_type-object_id-MAX_NUM_FORMS": "",
            "extra_views_tests-tag-content_type-object_id-0-name": "Test",
            "extra_views_tests-tag-content_type-object_id-1-DELETE": True,
        }

        res = self.client.post("/inlines/new/", data, follow=True)
        self.assertEqual(len(res.context["form"].errors), 0)
        self.assertEqual(len(res.context["inlines"][0].errors[0]), 2)
        self.assertEqual(res.context["view"].object, None)

    def test_update(self):
        order = Order(name="Dummy Order")
        order.save()

        item_ids = []
        for i in range(2):
            item = Item(
                name="Item %i" % i,
                sku=str(i) * 13,
                price=D("9.99"),
                order=order,
                status=0,
            )
            item.save()
            item_ids.append(item.id)

        tag = Tag(name="Test", content_object=order)
        tag.save()

        res = self.client.get("/inlines/{}/".format(order.id))

        self.assertEqual(res.status_code, 200)
        order = Order.objects.get(id=order.id)

        self.assertEqual(2, order.items.count())
        self.assertEqual("Item 0", order.items.all()[0].name)

        data = {
            "name": "Dummy Order",
            "items-TOTAL_FORMS": "4",
            "items-INITIAL_FORMS": "2",
            "items-MAX_NUM_FORMS": "",
            "items-0-name": "Bubble Bath",
            "items-0-sku": "1234567890123",
            "items-0-price": D("9.99"),
            "items-0-status": 0,
            "items-0-id": item_ids[0],
            "items-1-name": "Bubble Bath",
            "items-1-sku": "1234567890123",
            "items-1-price": D("9.99"),
            "items-1-status": 0,
            "items-1-id": item_ids[1],
            "items-2-name": "Bubble Bath",
            "items-2-sku": "1234567890123",
            "items-2-price": D("9.99"),
            "items-2-status": 0,
            "items-3-DELETE": True,
            "extra_views_tests-tag-content_type-object_id-TOTAL_FORMS": 3,
            "extra_views_tests-tag-content_type-object_id-INITIAL_FORMS": 1,
            "extra_views_tests-tag-content_type-object_id-MAX_NUM_FORMS": "",
            "extra_views_tests-tag-content_type-object_id-0-name": "Test",
            "extra_views_tests-tag-content_type-object_id-0-id": tag.id,
            "extra_views_tests-tag-content_type-object_id-0-DELETE": True,
            "extra_views_tests-tag-content_type-object_id-1-name": "Test 2",
            "extra_views_tests-tag-content_type-object_id-2-name": "Test 3",
        }

        res = self.client.post("/inlines/{}/".format(order.id), data)
        self.assertEqual(res.status_code, 302)
        # Test that the returned url is the same as the instances absolute url.
        self.assertEqual(res.url, order.get_absolute_url())

        order = Order.objects.get(id=order.id)

        self.assertEqual(3, order.items.count())
        self.assertEqual(2, Tag.objects.count())
        self.assertEqual("Bubble Bath", order.items.all()[0].name)

    def test_parent_instance_saved_in_form_save(self):
        order = Order(name="Dummy Order")
        order.save()

        data = {
            "name": "Dummy Order",
            "items-TOTAL_FORMS": "0",
            "items-INITIAL_FORMS": "0",
            "items-MAX_NUM_FORMS": "",
            "extra_views_tests-tag-content_type-object_id-TOTAL_FORMS": "0",
            "extra_views_tests-tag-content_type-object_id-INITIAL_FORMS": "0",
            "extra_views_tests-tag-content_type-object_id-MAX_NUM_FORMS": "",
        }

        res = self.client.post("/inlines/{}/".format(order.id), data)
        self.assertEqual(res.status_code, 302)

        order = Order.objects.get(id=order.id)
        self.assertTrue(order.action_on_save)

    def test_url_arg(self):
        """
        Regression test for #122: get_context_data should not be called with *args
        """
        res = self.client.get("/inlines/123/new/")
        self.assertEqual(res.status_code, 200)


class CalendarViewTests(TestCase):
    def test_create(self):
        event = Event(name="Test Event", date=datetime.date(2012, 1, 1))
        event.save()

        res = self.client.get("/events/2012/jan/")
        self.assertEqual(res.status_code, 200)


class SearchableListTests(TestCase):
    def setUp(self):
        order = Order(name="Dummy Order")
        order.save()
        Item.objects.create(
            sku="1A",
            name="test A",
            order=order,
            price=0,
            date_placed=datetime.date(2012, 1, 1),
        )
        Item.objects.create(
            sku="1B",
            name="test B",
            order=order,
            price=0,
            date_placed=datetime.date(2012, 2, 1),
        )
        Item.objects.create(
            sku="C",
            name="test",
            order=order,
            price=0,
            date_placed=datetime.date(2012, 3, 1),
        )

    def test_search(self):
        res = self.client.get("/searchable/", data={"q": "1A test"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(1, len(res.context["object_list"]))

        res = self.client.get("/searchable/", data={"q": "1Atest"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(0, len(res.context["object_list"]))

        # date search
        res = self.client.get("/searchable/", data={"q": "01.01.2012"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(1, len(res.context["object_list"]))

        res = self.client.get("/searchable/", data={"q": "02.01.2012"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(0, len(res.context["object_list"]))

        # search query provided by view's get_search_query method
        res = self.client.get(
            "/searchable/predefined_query/", data={"q": "idoesntmatter"}
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(1, len(res.context["object_list"]))

        # exact search query
        res = self.client.get("/searchable/exact_query/", data={"q": "test"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(1, len(res.context["object_list"]))

        # search query consists only of spaces
        res = self.client.get("/searchable/", data={"q": "  "})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(3, len(res.context["object_list"]))

        # wrong lookup
        try:
            self.assertRaises(
                self.client.get("/searchable/wrong_lookup/", data={"q": "test"})
            )
            error = False
        except ValueError:
            error = True
        self.assertTrue(error)


class SortableViewTest(TestCase):
    def setUp(self):
        order = Order(name="Dummy Order")
        order.save()
        Item.objects.create(sku="1A", name="test A", order=order, price=0)
        Item.objects.create(sku="1B", name="test B", order=order, price=0)

    def test_sort(self):
        res = self.client.get("/sortable/fields/")
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.context["sort_helper"].is_sorted_by_name())

        asc_url = res.context["sort_helper"].get_sort_query_by_name_asc()
        res = self.client.get("/sortable/fields/%s" % asc_url)
        self.assertEqual(res.context["object_list"][0].name, "test A")
        self.assertEqual(res.context["object_list"][1].name, "test B")
        self.assertTrue(res.context["sort_helper"].is_sorted_by_name())

        desc_url = res.context["sort_helper"].get_sort_query_by_name_desc()
        res = self.client.get("/sortable/fields/%s" % desc_url)
        self.assertEqual(res.context["object_list"][0].name, "test B")
        self.assertEqual(res.context["object_list"][1].name, "test A")
        self.assertTrue(res.context["sort_helper"].is_sorted_by_name())
        # reversed sorting
        sort_url = res.context["sort_helper"].get_sort_query_by_name()
        res = self.client.get("/sortable/fields/%s" % sort_url)
        self.assertEqual(res.context["object_list"][0].name, "test A")
        sort_url = res.context["sort_helper"].get_sort_query_by_name()
        res = self.client.get("/sortable/fields/%s" % sort_url)
        self.assertEqual(res.context["object_list"][0].name, "test B")
        # can't use fields and aliases in same time
        self.assertRaises(
            ImproperlyConfigured,
            lambda: self.client.get("/sortable/fields_and_aliases/"),
        )
        # check that aliases included in params
        res = self.client.get("/sortable/aliases/")
        self.assertIn(
            "o=by_name", res.context["sort_helper"].get_sort_query_by_by_name()
        )
        self.assertIn("o=by_sku", res.context["sort_helper"].get_sort_query_by_by_sku())
