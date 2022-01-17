from collections import OrderedDict
# py3
from builtins import str as unicode

from django import forms
from django import template
from django.db import models

from contactfield.fields import BaseContactField

from django.forms.forms import pretty_name

register = template.Library()


def contact_cards(obj, concise=True):
    """
    Get all the contact fields from a model or form and return them as cards
    """
    # Get all the fields. Try as a form first, then as a model.
    if isinstance(obj, models.Model):
        fields = [(field.name, field) for field in obj._meta.fields]
        value_getter = lambda field_name: getattr(obj, field_name)
    elif isinstance(obj, (forms.Form, forms.ModelForm)):
        fields = [(name, field) for (name, field) in obj.fields.iteritems()]
        if obj.is_valid():
            value_getter = lambda field_name: obj.cleaned_data[field_name]
        else:
            value_getter = lambda field_name: obj[field_name].value()
    else:
        return {}

    contact_card_dict = {}
    # for field_name, field in filter(lambda (field_name, field): isinstance(field, BaseContactField), fields):
    # for field_name, field in [(field_name, field) for pair in fields if isinstance(field, BaseContactField)]:
    for field_name, field in filter(lambda pair: isinstance(pair[1], BaseContactField), fields):
        values = value_getter(field_name)
        contact_card_dict[field_name] = {}
        for group in field._valid_groups:
            contact_card_dict[field_name][group] = OrderedDict()
            for label in field._valid_labels:
                value = values.get(group, {}).get(label, '')
                display_name = field.label_format.format(
                    field=unicode(field.display_name),
                    group=unicode(field.group_display_names.get(
                        group, pretty_name(group)
                    )),
                    label=unicode(field.label_display_names.get(
                        label, pretty_name(label)
                    ))
                )
                if value or not concise:
                    contact_card_dict[field_name][group][label] = {
                        'display_name': display_name,
                        'value': value
                    }

    return contact_card_dict


register.filter(contact_cards)
