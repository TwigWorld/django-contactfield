django-contactfield
===================

A flexible, customisable contact field for Django that can store different
address formats based on context.

To do
-----

 - Tests
 - Custom display names for labels
 - Custom validation / fields for labels


Usage
-----

Contactfield defines a field class (one for standard forms and one for model
forms), and a form mixin. You must use both to fully benefit from the module's
features.


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

There are two ways to customise contact field usage:

 - Define the valid groups and labels for a field
 - Limit which groups and labels are displayed on a particular form

###Defining your own groups and labels

A field's valid_groups and valid_labels defines the superset of values it can
contain. You can set it in one of two ways:

 - Subclass the contact field, and redefine valid_groups and valid_labels
 - Instantiate contact field and pass in any of the following arguments:
   * valid_groups
   * valid_labels
   * addtional_groups
   * additional_labels
   * exclude_groups
   * exclude_labels

Where the 'additional' and 'exclude' keywords modify the original properties of
the field. These values will be ignored if valid_groups or valid_fields are
also supplied as arguments.

The value of the field will always contain all valid groups and valid fields
as keys, even if values have not yet been set for them.

Any values that are supplied to the field that do not correspond to a valid
group/label pair will simply be ignored. This extra data is cleansed away and
no error is raised - this prevents headaches should you ever change the
groups or labels in a currently deployed app. But be aware if you remove
allowable labels, then any stored data for the field that uses those old
labels should be considered lost.

###Limiting groups and labels in forms

While the valid_groups and valid_labels parameters define all possible entries
that the contact field can contain, it is unlikely you would want to display
them all in a single form.

For example you may wish to display a form that shows only billing details
while simultaneously allowing the field to store other contact details.

Or you may wish to present different address labels to different users
depending on the user's country (for example state and zip code for US users).

To do this, simply pass in contact_group_subsets and contact_label_subsets
when instantiating the form. As a form may contain multiple contact fields,
these values need to be a dictionary for each field you wish to update.

```python

form = ContactForm(
    contact_group_subsets={'contact_info': ['personal']},
    contact_label_subsets={
        'contact_info': ['full_name', 'street_address', 'city', 'region', 'postal_code']
    },
)

```