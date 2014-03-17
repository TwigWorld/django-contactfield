from unittest import TestCase

from fields import BaseContactField, ContactFormField, ContactField


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
    pass


class TemplateTagsTest(TestCase):
    pass
