Views
=====

For all of these views we've tried to mimic the API of Django's existing class-based
views as closely as possible, so they should feel natural to anyone who's already
familiar with Django's views.


FormSetView
-----------

This is the formset equivalent of Django's FormView. Use it when you want to
display a single (non-model) formset on a page.

A simple formset::

    from extra_views import FormSetView
    from foo.forms import MyForm    
    

    class MyFormSetView(FormSetView):
        template_name = 'myformset.html'
        form_class = MyForm
        success_url = 'success/'

        def get_initial(self):
            # return whatever you'd normally use as the initial data for your formset.
          return data

        def formset_valid(self, formset):
            # do stuff
            return super(MyFormSetView, self).formset_valid(formset)

and in myformset.html::

    ...
    {{ formset }}
    ...

This view will render the template :code:`myformset.html` with a context variable
:code:`formset` representing the formset of MyForm. Once POSTed and successfully
validated, :code:`formset_valid` will be called which is where your handling logic
goes, then it redirects to :code:`success_url`.

FormSetView exposes all the parameters you'd normally be able to pass to the
:code:`FormSet` constructor and formset_factory. Example (using the default
settings)::

    class MyFormSetView(FormSetView):
        template_name = 'myformset.html'
        form_class = MyForm
        formset_class = MyFormSet
        initial = [{'name': 'foo'}, {'name', 'bar'}]
        prefix = 'myform'
        success_url = 'success/'
        factory_kwargs = {'extra': 2, 'max_num': None,
                          'can_order': False, 'can_delete': False}
        formset_kwargs = {'auto_id': 'my_id_%s'}
        ...


ModelFormSetView
----------------

ModelFormSetView makes use of Django's modelformset_factory, using the
declarative syntax used in FormSetView as well as Django's own class-based
views. So as you'd expect, the simplest usage is as follows::

    from extra_views import ModelFormSetView
    from foo.models import MyModel


    class MyModelFormSetView(ModelFormSetView):
        template_name = 'mymodelformset.html'
        model = MyModel

Like :code:`FormSetView`, the :code:`formset` variable is made available in the template
context. By default this will populate the formset with all the instances of
:code:`MyModel` in the database. You can control this by overriding :code:`get_queryset` on
the class, which could filter on a URL kwarg (:code:`self.kwargs`), for example::

    class MyModelFormSetView(ModelFormSetView):
        template_name = 'mymodelformset.html'
        model = MyModel

        def get_queryset(self):
            slug = self.kwargs['slug']
            return super(MyModelFormSetView, self).get_queryset().filter(slug=slug)

Optionally, :code:`fields` can be used to define the fields displayed in the
formset::

    class MyModelFormSetView(ModelFormSetView):
        template_name = 'mymodelformset.html'
        model = MyModel
        fields = ['name', 'date', 'slug']

:code:`exclude` can be set in an analogous way.


InlineFormSetView
-----------------

When you want to edit models related to a parent model (using a ForeignKey),
you'll want to use InlineFormSetView. An example use case would be editing user
reviews related to a product::

    from extra_views import InlineFormSetView


    class EditProductReviewsView(InlineFormSetView):
        model = Product
        inline_model = Review

        ...

Aside from the use of :code:`model` and :code:`inline_model`,
:code:`InlineFormSetView` works more-or-less in the same way as
:code:`ModelFormSetView`.


GenericInlineFormSetView
------------------------

You can also use generic relationships for your inline formsets, this makes use
of Django's :code:`generic_inlineformset_factory`. :code:`ct_field` and
:code:`fk_field` should be set in :code:`factory_kwargs` if they need to be
changed from their default values::

    from extra_views.generic import GenericInlineFormSetView


    class EditProductReviewsView(GenericInlineFormSetView):
        model = Product
        inline_model = Review
        factory_kwargs = {'ct_field': 'content_type', 'fk_field': 'object_id',
                          'max_num': 1}
        formset_kwargs = {'save_as_new': True}

        ...


CreateWithInlinesView and UpdateWithInlinesView
-----------------------------------------------

These are the most powerful views in the library, they are effectively
replacements for Django's own :code:`CreateView` and :code:`UpdateView`. The key difference is
that they let you include any number of inline formsets (as well as the parent
model's form), this provides functionality much like the Django Admin change
forms. The API should be fairly familiar as well. The list of the inlines will
be passed to the template as context variable `inlines`.

Here is a simple example that demonstrates the use of each view with both normal
inline relationships and generic inlines::

    from extra_views import InlineFormSetFactory, CreateWithInlinesView, UpdateWithInlinesView
    from extra_views.generic import GenericInlineFormSetFactory


    class ItemsInline(InlineFormSetFactory):
        model = Item
        fields = '__all__'


    class TagsInline(GenericInlineFormSetFactory):
        model = Tag
        fields = '__all__'


    class OrderCreateView(CreateWithInlinesView):
        model = Order
        inlines = [ItemsInline, TagsInline]
        fields = '__all__'

        def get_success_url(self):
            return self.object.get_absolute_url()


    class OrderUpdateView(UpdateWithInlinesView):
        model = Order
        form_class = OrderForm
        inlines = [ItemsInline, TagsInline]

        def get_success_url(self):
            return self.object.get_absolute_url()        

and in the html template::

    ...
    {{ form }}

    {% for formset in inlines %}
        {{ formset }}
    {% endfor %}
    ...

