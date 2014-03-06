import simplejson as json

from jsonfield.fields import JSONFormField, JSONField

from django import forms
from django.utils.translation import ugettext_lazy as _

from widgets import NullWidget


class BaseContactField(object):
    """
    A contact field allows contact information to be stored using a relatively
    loose ruleset in order to allow for many different contexts to be supported
    without creating multiple, complex address models.

    Contact data takes the form:

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
        concise=False,
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

        self._concise = concise

        if 'default' in kwargs:
            kwargs['default'] = self.as_dict(kwargs['default'])
        if 'initial' in kwargs:
            kwargs['initial'] = self.as_dict(kwargs['initial'])

        super(BaseContactField, self).__init__(*args, **kwargs)
        self.required = False

    def _initial_dict(self, initial=None):
        """
        Generate an initial contact dictionary for all valid groups and fields.
        If a dictionary of values is supplied, then these will be applied to
        the new dictionary.
        """
        if initial is None:
            initial = {}
        full_initial = {
            group: {
                label: '' if not initial.get(group, {}).get(label) else initial[group][label]
                for label in self.get_valid_labels()
            }
            for group in self.get_valid_groups()
        }
        if self.concise_mode():
            concise_initial = {}
            for group, labels in full_initial.iteritems():
                for label, value in labels.iteritems():
                    if value:
                        concise_initial.setdefault(group, {})[label] = value
            return concise_initial
        return full_initial

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

    def concise_mode(self):
        return self._concise


class ContactFormField(BaseContactField, JSONFormField):

    def __init__(self, *args, **kwargs):
        if not 'initial' in kwargs:
            kwargs['initial'] = {}
        # Always override widget
        kwargs['widget'] = NullWidget
        super(ContactFormField, self).__init__(*args, **kwargs)

    def bound_data(self, data, initial):
        # This field is never updated directly in a form
        return initial

    def clean(self, value):
        value = super(BaseContactField, self).clean(value)
        return self.as_dict(value)


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
