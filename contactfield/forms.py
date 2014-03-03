from functools import partial

from django import forms

from fields import _ContactFieldFormField


class ContactFieldFormMixin(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ContactFieldFormMixin, self).__init__(*args, **kwargs)

        # Find all the contact fields, and create dynamic fields
        self._contact_fields = {}
        for field_name, field in filter(
            lambda field: isinstance(field[1], _ContactFieldFormField),
            self.fields.iteritems()
        ):
            field.hidden = True
            self._contact_fields[field_name] = {
                'model_field': field.model_field,
                'pseudo_fields': {}
            }
            for valid_group in field.model_field.valid_groups:
                for valid_label in field.model_field.valid_labels:
                    pseudo_field_name = '%s__%s__%s' % (field_name, valid_group, valid_label)
                    if getattr(self.instance, field_name, None):
                        initial = getattr(self.instance, field_name).get(valid_group, {}).get(valid_label)
                    else:
                        initial = None
                    charfield = forms.CharField(required=False, initial=initial)
                    self.fields[pseudo_field_name] = charfield
                    self._contact_fields[field_name]['pseudo_fields'][pseudo_field_name] = charfield

    def __getattribute__(self, name, *args, **kwargs):
        if name[:6] == 'clean_' and name[6:] in self._contact_fields.keys():
            return partial(self._clean_CONTACTFIELD, name[6:])
        return super(ContactFieldFormMixin, self).__getattribute__(name, *args, **kwargs)

    def _clean_CONTACTFIELD(self, contact_field_name):
        cleaned_data = {}
        for pseudo_field_name, field in self._contact_fields[contact_field_name]['pseudo_fields'].iteritems():
            pseudo_field_value = self.data.get(pseudo_field_name)
            if pseudo_field_value:
                field_name, group, label = pseudo_field_name.split('__')
                cleaned_data.setdefault(group, {})[label] = pseudo_field_value
        return cleaned_data
