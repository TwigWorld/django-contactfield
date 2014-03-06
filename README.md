django-contactfield
===================

A flexible, customisable contact field for Django that can store different
address formats based on context.

To do
-----

 - Tests
 - Custom validation / fields for labels


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

There are three ways to customise contact field usage:

 - Define the valid groups and labels for a field
 - Limit which groups and labels are displayed on a particular form
 - Contol how the field labels are displayed

The former defines the superset of values that a contact field can contain
- in other words all groups and labels for all scenarios that the field is
likely to be used in.

The latter allows you to create forms for a specific subset of allowed groups
and labels, without changing or otherwise restricting the values that the
field itself can store.

###Defining your own groups and labels

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
    contact_group_subsets={'contact_info': ['personal']},
    contact_label_subsets={
        'contact_info': ['full_name', 'street_address', 'city', 'region', 'postal_code']
    },
)

# Creates the following fields:
#     contact_info__personal__full_name
#     contact_info__personal__street_address
#     contact_info__personal__city
#     contact_info__personal__region
#     contact_info__personal__postal_code

```

### Controlling how labels are displayed

The default output for a label is **group: label** where group is the group
name and label is the label name (capitalised and with underscores replaced).

To change this format, simply update the **contact_label_format** property of
the form (valid parameters are field, group and label).

```python

# Examples

contact_label_format = "[{field} ({group})]: {label}"
contact_label_format = "{label}"

```

When you are happy with the output format, you can also provide alternative
display names for any field, group or label value by updating the following
properties:

 - contact_field_display_names
 - contact_group_display_names
 - contact_label_display_names

Each is a dictionary, mapping a name to a displayable output. You can provide
lazy translatable values if you wish.

```python

# Example

contact_label_display_names = {
  'full_name': _("Name"),
  'telephone': _("Telephone number")
  ...
}

```

Obviously you would only need to provide values for the parameters you are
actually outputting.