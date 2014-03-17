from unittest import TestCase

from django import forms

from fields import BaseContactField, ContactFormField, ContactField
from forms import ContactFieldFormMixin


class FormFieldTest(TestCase):

    field_class = ContactFormField

    def test_defaults(self):
        field = self.field_class()
        self.assertEquals(
            field._valid_groups,
            list(BaseContactField.valid_groups)
        )
        self.assertEquals(
            field._valid_labels,
            list(BaseContactField.valid_labels)
        )
        self.assertEquals(
            field.label_format,
            BaseContactField.label_format
        )
        self.assertEquals(
            field.display_name,
            BaseContactField.display_name
        )
        self.assertEquals(
            field.group_display_names,
            BaseContactField.group_display_names
        )
        self.assertEquals(
            field.label_display_names,
            BaseContactField.label_display_names
        )
        self.assertEquals(
            field.concise_mode(),
            False
        )

    def test_overrides(self):
        field = self.field_class(
            valid_groups=['a', 'b'],
            valid_labels=['1', '2'],
            label_format='{label}',
            display_name='Name',
            concise=True
        )
        self.assertEquals(
            field._valid_groups,
            ['a', 'b']
        )
        self.assertEquals(
            field._valid_labels,
            ['1', '2']
        )
        self.assertEquals(
            field.label_format,
            '{label}'
        )
        self.assertTrue(
            isinstance(field.label_format, unicode)
        )
        self.assertEquals(
            field.display_name,
            'Name'
        )
        self.assertEquals(
            field.concise_mode(),
            True
        )

    def test_updates(self):
        field = self.field_class(
            additional_groups=['test'],
            additional_labels=['test'],
            exclude_groups=['billing'],
            exclude_labels=['salutation'],
            update_group_display_names={'test': 'Test'},
            update_label_display_names={'full_name': 'Test'}
        )
        new_valid_groups = list(BaseContactField.valid_groups)
        new_valid_groups.remove('billing')
        new_valid_groups.append('test')
        self.assertNotEquals(
            field._valid_groups,
            BaseContactField.valid_groups
        )
        self.assertEquals(
            set(field._valid_groups),
            set(new_valid_groups)
        )
        new_valid_labels = list(BaseContactField.valid_labels)
        new_valid_labels.remove('salutation')
        new_valid_labels.append('test')
        self.assertNotEquals(
            field._valid_labels,
            BaseContactField.valid_labels
        )
        self.assertEquals(
            set(field._valid_labels),
            set(new_valid_labels)
        )

    def test_output(self):
        field = self.field_class(
            valid_groups=['test_group'],
            valid_labels=['test_label']
        )
        self.assertEquals(
            field.as_dict(None),
            {'test_group': {'test_label': ''}}
        )
        field._concise = True
        self.assertEquals(
            field.as_dict(None),
            {}
        )
        self.assertEquals(
            field.as_dict({
                'test_group': {
                    'test_label': 'Success',
                    'no_such_label': 'Failure'
                }
            }),
            {'test_group': {'test_label': 'Success'}}
        )


class ModelFieldTest(FormFieldTest):

    field_class = ContactField

    def test_formfield(self):
        field = ContactField(
            valid_groups=['test'],
            valid_labels=['test'],
            label_format='{label}',
            display_name='Test',
            concise=True
        )
        form_field = field.formfield()

        self.assertEquals(
            field.default,
            form_field.initial
        )
        self.assertEquals(
            set(field.valid_groups),
            set(form_field.valid_groups)
        )
        self.assertEquals(
            set(field.valid_labels),
            set(form_field.valid_labels)
        )
        self.assertEquals(
            field.label_format,
            form_field.label_format
        )
        self.assertEquals(
            field.display_name,
            form_field.display_name
        )
        self.assertEquals(
            field.group_display_names,
            form_field.group_display_names
        )
        self.assertEquals(
            field.label_display_names,
            form_field.label_display_names
        )
        self.assertEquals(
            field._concise,
            form_field._concise
        )


class FormMixinTest(TestCase):

    def setUp(self):
        class ContactForm(ContactFieldFormMixin, forms.Form):

            contact_group_subsets = {
                'contact_field': ['group_1', 'group_2']
            }

            contact_label_subsets = {
                'contact_field': ['label_1', 'label_2']
            }

            contact_field_kwargs = {
                'contact_field__group_1__label_1': {
                    'field': forms.IntegerField,
                    'required': True
                }
            }

            contact_field = ContactFormField(
                valid_groups=['group_1', 'group_2', 'group_3'],
                valid_labels=['label_1', 'label_2', 'label_3'],
                concise=True
            )
        self.form_class = ContactForm

    def test_pseudo_fields(self):
        form = self.form_class()
        self.assertEquals(
            set(
                [
                    'contact_field',
                    'contact_field__group_1__label_1',
                    'contact_field__group_1__label_2',
                    'contact_field__group_2__label_1',
                    'contact_field__group_2__label_2',
                ]
            ),
            set(form.fields.keys())
        )

    def test_field_kwargs(self):
        form = self.form_class()
        self.assertEquals(
            form.fields['contact_field__group_1__label_1'].__class__,
            forms.IntegerField
        )
        self.assertTrue(
            form.fields['contact_field__group_1__label_1'].required,
        )
        self.assertFalse(
            form.fields['contact_field__group_1__label_2'].required,
        )

    def test_form_field_updated(self):
        form = self.form_class(data={'contact_field__group_1__label_1': '1'})
        self.assertEquals(
            form['contact_field'].value(),
            {}
        )
        self.assertTrue(form.is_valid())
        self.assertEquals(
            form.cleaned_data['contact_field'],
            {'group_1': {'label_1': '1'}}
        )


class TemplateTagsTest(TestCase):
    pass
