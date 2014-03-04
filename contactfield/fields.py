import simplejson as json

from jsonfield.fields import JSONFormField, JSONField

from django import forms
from django.utils.translation import ugettext_lazy as _


def contact_field_as_dict(value):

    if value and isinstance(value, (unicode, str)):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            value = {}

    if not isinstance(value, dict):
        value = {}

    return value


class BaseContactField(object):
    """
    A contact field allows contact information to be stored using a relatively
    loose ruleset in order to allow for many different contexts to be supported
    without creating multiple, complex address models.

    The field validates that supplied information is in the form:

    {
        <group>: {
            <label>: <value>
            ...
        }
        ...
    }

    where group and label are part of the field's valid groups and labels,
    and value is a basic type (integer, string, boolean or null)
    """
    valid_groups = [
        'business',
        'billing',
        'home',
        'personal',
        'school',
        'shipping',
        'work'
    ]

    valid_labels = [
        # Name
        'salutation',
        'full_name',
        'first_name',
        'middle_names',
        'last_name',
        'maiden_name',
        'company_name',
        'job_title',
        # Telephone
        'phone',
        'mobile',
        'fax',
        'do_not_call',
        # Email
        'email',
        'do_not_email',
        # Website
        'website',
        # Address
        'address_1',
        'address_2',
        'address_3',
        'address_4',
        'address_5',
        'address_6',
        'address_7',
        'address_8',
        'address_9',
        'building',
        'street_address',
        'city',
        'region',
        'state',
        'country',
        'state',
        'postal_code',
        # Other
        'notes'
    ]

    def __init__(
        self,
        valid_groups=None,
        valid_labels=None,
        additional_groups=None,
        additional_labels=None,
        exclude_groups=None,
        exclude_labels=None,
        *args,
        **kwargs
    ):
        super(BaseContactField, self).__init__(*args, **kwargs)

        if valid_groups is not None:
            self.valid_groups = list(valid_groups)
        else:
            if additional_groups is not None:
                self.valid_groups = list(set(self.valid_groups) | set(additional_groups))
            if exclude_groups is not None:
                self.valid_groups = list(set(self.valid_groups) - set(exclude_groups))

        if valid_labels is not None:
            self.valid_labels = list(valid_labels)
        else:
            if additional_labels is not None:
                self.valid_labels = list(set(self.valid_labels) | set(additional_labels))
            if exclude_labels is not None:
                self.valid_labels = list(set(self.valid_labels) - set(exclude_labels))

    def validate(self, value, *args, **kwargs):

        contact_groups = contact_field_as_dict(value)

        if not isinstance(contact_groups, dict):
            raise forms.ValidationError(
                _("Contact groups are not in correct format.")
            )

        group_keys = contact_groups.keys()
        if not set(group_keys) <= set(self.valid_groups):
            raise forms.ValidationError(_("Invalid contact group supplied."))

        for group_key in group_keys:
            contact_labels = contact_groups[group_key]
            if not isinstance(contact_labels, dict):
                raise forms.ValidationError(
                    _("Contact labels are not in correct format.")
                )
            label_keys = contact_labels.keys()
            if not set(label_keys) <= set(self.valid_labels):
                raise forms.ValidationError(_("Invalid contact label supplied."))

            for label_key in label_keys:
                label_value = contact_labels[label_key]
                if not isinstance(label_value, (int, str, unicode, bool, None.__class__)):
                    raise forms.ValidationError(_("Invalid contact value supplied."))

        return contact_groups


class ContactFormField(BaseContactField, JSONFormField):

    def __init__(self, *args, **kwargs):
        if not 'initial' in kwargs:
            kwargs['initial'] = {}
        if not 'widget' in kwargs:
            kwargs['widget'] = forms.HiddenInput
        super(ContactFormField, self).__init__(*args, **kwargs)


class ContactField(BaseContactField, JSONField):

    def __init__(self, *args, **kwargs):
        if not 'default' in kwargs:
            kwargs['default'] = {}
        super(ContactField, self).__init__(*args, **kwargs)


    def formfield(self, **kwargs):
        defaults = {
            'form_class': ContactFormField,
            'valid_groups': self.valid_groups,
            'valid_labels': self.valid_labels,
            'widget': forms.HiddenInput
        }
        defaults.update(kwargs)
        return super(ContactField, self).formfield(**defaults)
