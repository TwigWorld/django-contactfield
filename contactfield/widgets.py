from django.forms.widgets import Widget


class NullWidget(Widget):
    """
    A simple hidden widget that renders nothing. Useful if we want to keep a
    field in a form, but not present any means of updating it directly.
    """
    is_hidden = True

    def render(self, *args, **kwargs):
        return ''
