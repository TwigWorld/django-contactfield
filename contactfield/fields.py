import simplejson as json

from jsonfield.fields import JSONFormField, JSONField

from django import forms
from django.utils.translation import ugettext_lazy as _


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
    valid_groups = (
        'business',
        'billing',
        'home',
        'personal',
        'school',
        'shipping',
        'work'
    )

    valid_labels = (
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
    )

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

        if valid_groups is not None:
            self._valid_groups = list(valid_groups)
        else:
            self._valid_groups = list(self.valid_groups)
            if additional_groups is not None:
                self._valid_groups = list(set(self._valid_groups) | set(additional_groups))
            if exclude_groups is not None:
                self._valid_groups = list(set(self._valid_groups) - set(exclude_groups))

        if valid_labels is not None:
            self._valid_labels = list(valid_labels)
        else:
            self._valid_labels = list(self.valid_labels)
            if additional_labels is not None:
                self.valid_labels = list(set(self._valid_labels) | set(additional_labels))
            if exclude_labels is not None:
                self.valid_labels = list(set(self._valid_labels) - set(exclude_labels))

        if 'default' in kwargs:
            kwargs['default'] = self.as_dict(kwargs['default'])
        if 'initial' in kwargs:
            kwargs['initial'] = self.as_dict(kwargs['initial'])

        super(BaseContactField, self).__init__(*args, **kwargs)

    def _initial_dict(self, initial=None):
        """
        Generate an initial contact dictionary for all valid groups and fields.
        If a dictionary of values is supplied, then these will be applied to
        the new dictionary.
        """
        if initial is None:
            initial = {}
        return {
            group: {
                label: '' if not initial.get(group, {}).get(label) else initial[group][label]
                for label in self.get_valid_labels()
            }
            for group in self.get_valid_groups()
        }

    def as_dict(self, value):
        """
        Return the contact field as a dictionary of groups and labels. If any
        formatting issues are encountered with the value, then a blank initial
        dictionary will be returned.
        """
        if value and isinstance(value, (unicode, str)):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                return self._initial_dict()

        if not isinstance(value, dict):
            return self._initial_dict()

        return self._initial_dict(value)

    def get_valid_groups(self):
        return self._valid_groups

    def get_valid_labels(self):
        return self._valid_labels

    def clean(self, value):
        value = super(BaseContactField, self).clean(value)
        return self.as_dict(value)


class ContactFormField(BaseContactField, JSONFormField):

    def __init__(self, *args, **kwargs):
        if not 'initial' in kwargs:
            kwargs['initial'] = {}
        super(ContactFormField, self).__init__(*args, **kwargs)


class ContactField(BaseContactField, JSONField):

    def __init__(self, *args, **kwargs):
        if not 'default' in kwargs:
            kwargs['default'] = {}
        super(ContactField, self).__init__(*args, **kwargs)


    def formfield(self, **kwargs):
        defaults = {
            'form_class': ContactFormField,
            'valid_groups': self.get_valid_groups(),
            'valid_labels': self.get_valid_labels()
        }
        defaults.update(kwargs)
        return super(ContactField, self).formfield(**defaults)
