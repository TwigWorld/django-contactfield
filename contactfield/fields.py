import json
# python 3
from builtins import str as unicode

from django.utils.translation import pgettext_lazy as _p, ugettext_lazy as _

from jsonfield.fields import JSONFormField, JSONField

from .utils import AccessDict, CastOnAssign
from .widgets import NullWidget


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

    label_format = u'{group}: {label}'

    display_name = _('Contact information')

    group_display_names = {
        'business': _('Business'),
        'billing': _('Billing'),
        'home': _p('Home user', 'Home'),
        'personal': _('Personal'),
        'school': _('School'),
        'shipping': _('Shipping'),
        'work': _('Work')
    }

    label_display_names = {
        # Name
        'salutation': _('Salutation'),
        'full_name': _('Full name'),
        'first_name': _('First name'),
        'middle_names': _('Middle names'),
        'last_name': _('Last name'),
        'maiden_name': _('Maiden name'),
        'company_name': _('Company name'),
        'job_title': _('Job title'),
        # Telephone
        'phone': _('Phone'),
        'mobile': _('Mobile'),
        'fax': _('Fax'),
        'do_not_call': _('Do not call'),
        # Email
        'email': _('Email'),
        'do_not_email': _('Do not Email'),
        # Website
        'website': _('Website'),
        # Address
        'address_1': _('Address (line 1)'),
        'address_2': _('Address (line 2)'),
        'address_3': _('Address (line 3)'),
        'address_4': _('Address (line 4)'),
        'address_5': _('Address (line 5)'),
        'address_6': _('Address (line 6)'),
        'address_7': _('Address (line 7)'),
        'address_8': _('Address (line 8)'),
        'address_9': _('Address (line 9)'),
        'building': _('Building'),
        'street_address': _('Street address'),
        'city': _('City'),
        'region': _('Region'),
        'state': _('State'),
        'country': _('Country'),
        'state': _('State'),
        'postal_code': _('Postal code'),
        # Other
        'notes': _('Notes')
    }

    def __init__(
        self,
        valid_groups=None,
        valid_labels=None,
        additional_groups=None,
        additional_labels=None,
        exclude_groups=None,
        exclude_labels=None,
        label_format=None,
        display_name=None,
        update_group_display_names=None,
        update_label_display_names=None,
        concise=False,
        *args,
        **kwargs
    ):
        # Groups and labels

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
                self._valid_labels = list(set(self._valid_labels) | set(additional_labels))
            if exclude_labels is not None:
                self._valid_labels = list(set(self._valid_labels) - set(exclude_labels))

        # Label format and displayable names
        if label_format is not None:
            self.label_format = unicode(label_format)
        if display_name is not None:
            self.display_name = display_name

        if update_group_display_names is not None:
            combined_group_display_names = {}
            combined_group_display_names.update(self.group_display_names)
            combined_group_display_names.update(update_group_display_names)
            self.group_display_names = combined_group_display_names

        if update_label_display_names is not None:
            combined_label_display_names = {}
            combined_label_display_names.update(self.label_display_names)
            combined_label_display_names.update(update_label_display_names)
            self.label_display_names = combined_label_display_names

        # Output format

        self._concise = concise

        # Initial values

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
            for group, labels in full_initial.items():
                for label, value in labels.items():
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

    def contribute_to_class(self, cls, name):
        """
        This ensures that the model that the field belongs to is able to set the
        field's value through the `to_python` method
        """
        super(ContactField, self).contribute_to_class(cls, name)
        setattr(cls, name, CastOnAssign(self))

    def get_default(self):
        default = super(ContactField, self).get_default()
        if isinstance(default, dict):
            return AccessDict.prepare(default)
        return default

    def from_db_value(self, value, expression, connection, context):
        value = super(ContactField, self).from_db_value(value, expression, connection, context)
        if isinstance(value, dict):
            return AccessDict.prepare(value)
        return value

    def to_python(self, value):
        value = super(ContactField, self).to_python(value)
        if isinstance(value, dict):
            return AccessDict.prepare(value)
        return value

    def formfield(self, **kwargs):
        defaults = {
            'form_class': ContactFormField,
            'valid_groups': self.get_valid_groups(),
            'valid_labels': self.get_valid_labels(),
            'label_format': self.label_format,
            'display_name': self.display_name,
            'update_group_display_names': self.group_display_names,
            'update_label_display_names': self.label_display_names,
            'concise': self._concise,
        }
        defaults.update(kwargs)
        return super(ContactField, self).formfield(**defaults)
