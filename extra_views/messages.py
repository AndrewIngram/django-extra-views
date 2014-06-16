from django.contrib import messages


class SuccessMessageWithInlinesMixin(object):
    """
    Adds a success message on successful form submission.
    """
    success_message = ''

    def forms_valid(self, form, inlines):
        response = super(SuccessMessageWithInlinesMixin, self).forms_valid(form, inlines)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data
