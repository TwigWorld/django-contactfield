from fields import ContactField, ContactFormField
from forms import ContactFieldFormMixin

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^contactfield\.fields\.(ContactField)"])
except ImportError:
    pass
