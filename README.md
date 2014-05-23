django-contactfield
===================

A flexible, customisable contact field for Django that can store different
address formats based on context.

Usage
-----

Contactfield defines a field class (one for standard forms and one for model
forms), and a form mixin. You must use both together to fully benefit from the
module's features.


###Basic Form example

```python

from django import forms

from contactfield.fields import ContactFormField
from contactfield.forms import ContactFieldFormMixin


class ContactForm(ContactFieldFormMixin, forms.Form):
    contact_info = ContactFormField()

```

###Basic ModelForm example

```python

from django import forms
from django.db import models

from contactfield.fields import ContactField
from contactfield.forms import ContactFieldFormMixin


class ContactModel(models.Model):
    ...
    contact_info = ContactField()
    ...


class ContactModelForm(ContactFieldFormMixin, forms.ModelForm):

    class Meta:
       model = ContactModel

```

How it works
------------

The value of a contact field is a two-level dictionary object that contains
keys for all the valid contact groups and labels of that field. Groups are
collections such as billing address and home address, while labels are the
specific fields within a group, such as name and country.

The default implementation contains a broad range of groups and labels to let
you get started as quickly as possible, however you will probably want to
customise these defaults (see Customisation).

When a form is generated using the mixin, all contact fields are analysed and
a series of psedudo fields are created in the form field__group__label, e.g.
contact_field__home__full_name

The actual contact field itself is not displayed, nor does it accept data
from the form. It is updated only by the pseudo fields that are present.

Customisation
-------------

There are several ways to customise contact field usage:

 - Define the valid groups and labels for a field
 - Limit which groups and labels are displayed on a particular form
 - Contol how the field labels are displayed
 - Manipulate the field behabiour for a contact field label
 - Change the way the field returns its value

###Defining your own groups and labels

A contact field's valid groups and labels defines the superset of values that
it can contain - in other words all groups and labels for all scenarios that
the field is likely to be used in.

You can set these in one of two ways:

 - Subclass the contact field, and redefine valid_groups and valid_labels
 - Instantiate the contact field and pass in any of the following arguments:
   * valid_groups
   * valid_labels
   * addtional_groups
   * additional_labels
   * exclude_groups
   * exclude_labels

Where the 'additional' and 'exclude' keywords modify the original properties of
the field. These values will be ignored if valid_groups or valid_fields are
also supplied as arguments.

The stored value of the field will always contain all valid groups and valid
fields as keys (even if values have not yet been set for them).

Any values that are supplied to the field that do not correspond to a valid
group/label pair will simply be ignored. This extra data is cleansed away and
no error is raised - this prevents headaches should you ever change the
groups or labels in a currently deployed app. But be aware if you remove
allowable labels, then any stored data for those labels should be considered lost.

```python

contact_field = ContactField(
    valid_groups=['personal', 'work'],
    valid_labels=['role', 'phone', 'email'],
    default={'personal': {'role': 'N/A'}}
)

# Default contact with all the available labels the field can store

{
    'personal': {
        'role': 'N/A',
        'email': '',
        'phone': ''
    },
    'work': {
        'role': '',
        'email': '',
        'phone': ''
    },
}

```

###Limiting groups and labels in forms

While the valid_groups and valid_labels parameters define **all** possible entries
that the contact field can contain, it is unlikely you would want to display
them all in a single form.

For example you may wish to display a form that shows only billing details
while simultaneously allowing the field to store other contact details.

Or you may wish to present different address labels to different users
depending on the user's country (for example state and zip code for US users).

To do this, simply pass in contact_group_subsets and contact_label_subsets
when instantiating the form. Because a form may contain multiple contact fields,
these values need to be a dictionary, with a key for each field you wish to update.

```python

form = ContactForm(
    contact_group_subsets={
      'contact_info': ['personal']
    },
    contact_label_subsets={
        'contact_info': ['full_name', 'street_address', 'city', 'region', 'postal_code']
    },
)

# Assuiming you have a field called contact_info, creates the following fields:
#     contact_info__personal__full_name
#     contact_info__personal__street_address
#     contact_info__personal__city
#     contact_info__personal__region
#     contact_info__personal__postal_code

```

### Controlling how labels are displayed

The default output for a label is **group: label** where group is the group
name and label is the label name (capitalised and with underscores replaced).

To change this format, simply pass the **label_format** argument to the contact
field (valid parameters are field, group and label).

```python

# Examples

# "[Contact (billing)]: Full name"
confactfield = ContactField(label_format='{field} ({group})]: {label}'')

```

When you are happy with the output format, you can also provide alternative
display names for any field, group or label value by passing the following
arguments:

 - display_name
 - update_group_display_names
 - update_label_display_names

Each is a dictionary, mapping a name to a displayable output. You can provide
lazy translatable values if you wish. In fact these are already supplied for
all the existing labels (hence the update part of the argument name).

```python

# Example

confactfield = ContactField(
    update_label_display_names = {
        'full_name': _("Name"),
        'phone': _("Telephone number")
    }

```

### Manipulating label field behaviour

By default, any pseudo field created by the contact field form will be of type
CharField and a value is not required to validate the form.

It is straightforward to change the field, validation, widget or other property
of the field by changing the form's **contact_label_kwargs** property.

This property is a dictionary of pseudo field names and the keyword arguments
you wish to pass to its field, with an additional keyword argument for changing
the field class itself.

```python

# Example

contact_label_kwargs = {
    'contact_info__personal__full_name': {
        'required': True
    },
    'contact_info__personal__email': {
        'field': forms.EmailField,
        'required': True,
    },
    'contact_info__billing__notes': {
        'widget': forms.Textarea
    }
}

```

### Changing the field's data output

By default, a contactifeld form will return a dictionary containing all possible
values that it can store, even if those values are empty. If you set concise
to True when instantiating the field, it will only return a dictionary with
values that have actually been set.

This is useful if you just need to print out the contents and aren't too worried
about missing keys.


Advanced examples
-----------------

### An order form using Crispy Forms

```python

class QuoteForm(ContactFieldFormMixin, forms.Form):

    contact_label_format = '{label}'

    contact_label_kwargs = {
        'contact_info__personal__full_name': {
            'required': True
        },
        'contact_info__personal__email': {
            'field': forms.EmailField,
            'required': True,
        },
        'contact_info__billing__notes': {
            'widget': forms.Textarea
        }
    }

    contact_info = ContactFormField(concise=True)

    quote_type = forms.ChoiceField(
        choices=(
            ('individual', _('Individual')),
            ('school', _('School')),
            ('business', _('Business')),
        ),
        label=_('Quote type')
    )

    def __init__(self, *args, **kwargs):
        super(QuoteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_class = 'col-xs-2'
        self.helper.field_class = 'col-xs-10'
        self.helper.layout = Layout(
            Fieldset(
                '',
                Field('quote_type'),
            ),
            Fieldset(
                _('Contact details'),
                Field('contact_info__personal__full_name'),
                Field('contact_info__personal__email'),
                Field('contact_info__personal__phone'),
                Field('contact_info__personal__country'),
            ),
            Fieldset(
                _('School details'),
                Field('contact_info__school__company_name'),
                Field('contact_info__school__address_1'),
                Field('contact_info__school__address_2'),
                Field('contact_info__school__address_3'),
                Field('contact_info__school__address_4'),
                Field('contact_info__school__website'),
            ),
            Fieldset(
                _('Company details'),
                Field('contact_info__school__company_name'),
                Field('contact_info__business__address_1'),
                Field('contact_info__business__address_2'),
                Field('contact_info__business__address_3'),
                Field('contact_info__business__address_4'),
                Field('contact_info__business__website'),
            ),
            Fieldset(
                _('Notes'),
                Field('contact_info__billing__notes')
            ),
            ButtonHolder(
                Submit('submit', _('Submit'))
            )
        )

```

Template tags
-------------

### contact_cards

If you need to output the value of a contact field outside of a form, complete
with translated labels, then you can use the contact cards filter.

Simply use it with a form instance or model instance that contains one or more
contact fields, and it will return a dictionary broken down into field names,
groups and labels (ordered) for the form or model.

By default, this will only return populated fields. If you want to return all
fields, then pass in concise=False

```html

# Example

load contactfield_tags

{% with obj|contact_cards as contact_cards %}
    {{ contact_cards.contact_field.billing }}
    <!-- OrderedDict([('full_name', {'display_name': u'Full name', 'value': u'Anonymous'}), ...]) -->
    {{ contact_cards.contact_field.billing.display_name }}: {{ contact_cards.contact_field.billing.value }}
    <!-- Name (Billing): Anonymous-->
{% endwith %}

```
