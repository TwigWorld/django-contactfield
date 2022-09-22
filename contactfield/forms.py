from functools import partial

from django import forms
from django.forms.forms import pretty_name
from django.utils.translation import ugettext_lazy as _

from .fields import ContactFormField

# python 3
from builtins import str as unicode


class ContactFieldFormMixin(object):
    """
    Provides the necessary form logic for generating pseudo fields for a
    contact field object. Each contact field object in the form will receive
    a set of fields, for all valid groups and labels for that field.

    If you wish to create a form using only a subset of the valid fields, then
    provide this using the contact_group_subsets and contact_label_subsets
    arguments:

    contact_group_subsets = {
        'main_contact': ['business']
        'billing_contact': ['billing'],
    }
    contact_label_subsets = {
        'main_contact': ['full_name', 'company_name', 'phone']
    }

    Note that existing values for valid fields that have been left off the form
    will be left intact, so you can, for example, create a seperate model form
    for billing and personal details using the same field.
    """
    contact_group_subsets = {}
    contact_label_subsets = {}
    contact_field_kwargs = {}

    def __init__(
        self,
        contact_group_subsets=None,
        contact_label_subsets=None,
        contact_field_kwargs=None,
        *args,
        **kwargs
    ):
        super(ContactFieldFormMixin, self).__init__(*args, **kwargs)

        # Find all the contact fields, and create dynamic fields based on
        # valid_groups and valid_labels, filtered by relevant subsets
        if contact_group_subsets is None:
            contact_group_subsets = self.contact_group_subsets
        if contact_label_subsets is None:
            contact_label_subsets = self.contact_label_subsets

        # Get a mapping of required fields and widgets
        if contact_field_kwargs is None:
            contact_field_kwargs = self.contact_field_kwargs

        self._contact_pseudo_fields = {}
        pseudo_fields = {}
        for field_name, field in filter(lambda pair: isinstance(pair[1], ContactFormField), self.fields.items()):
            valid_groups_for_field = contact_group_subsets.get(field_name)
            valid_labels_for_field = contact_label_subsets.get(field_name)
            valid_groups = [group for group in field.get_valid_groups() if valid_groups_for_field is None or group in valid_groups_for_field]
            valid_labels = [label for label in field.get_valid_labels() if valid_labels_for_field is None or label in valid_labels_for_field]

            self._contact_pseudo_fields[field_name] = {}
            for valid_group in valid_groups:
                for valid_label in valid_labels:
                    pseudo_field_name = '%s__%s__%s' % (field_name, valid_group, valid_label)
                    field_kwargs = {}
                    field_kwargs.update(contact_field_kwargs.get(pseudo_field_name, {}))
                    FieldClass = field_kwargs.pop('field', forms.CharField)
                    if not 'required' in field_kwargs:
                        field_kwargs['required'] = False
                    if self[field_name].value() is not None:
                        initial = self.fields[field_name].as_dict(
                            self[field_name].value()
                        ).get(valid_group, {}).get(valid_label)
                    else:
                        initial = None

                    pseudo_field = FieldClass(
                        initial=initial,
                        label=field.label_format.format(
                            field=unicode(field.display_name),
                            group=unicode(field.group_display_names.get(
                                valid_group, pretty_name(valid_group)
                            )),
                            label=unicode(field.label_display_names.get(
                                valid_label, pretty_name(valid_label)
                            ))
                        ),
                        **field_kwargs
                    )

                    pseudo_fields[pseudo_field_name] = pseudo_field
                    self._contact_pseudo_fields[field_name][pseudo_field_name] = pseudo_field
        self.fields.update(pseudo_fields)

    def __getattribute__(self, name, *args, **kwargs):
        if name[:6] == 'clean_' and name[6:] in self._contact_pseudo_fields.keys():
            return partial(self._clean_CONTACTFIELD, name[6:])
        return super(ContactFieldFormMixin, self).__getattribute__(name, *args, **kwargs)

    def _clean_CONTACTFIELD(self, contact_field_name):
        """
        Find all the psueduo fields for a contact field in form data, and use
        them to update the main field.
        """
        cleaned_data = self.fields[contact_field_name].as_dict(
            self[contact_field_name].value()
        )
        for pseudo_field_name, field in self._contact_pseudo_fields[contact_field_name].items():
            pseudo_field_value = self.data.get(pseudo_field_name, None)
            if pseudo_field_value is not None:
                if pseudo_field_value or not self.fields[contact_field_name].concise_mode():
                    field_name, group, label = pseudo_field_name.split('__')
                    cleaned_data.setdefault(group, {})[label] = pseudo_field_value
        return cleaned_data
