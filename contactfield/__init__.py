from fields import ContactField, ContactFormField

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^contactfield\.fields\.(ContactField)"])
except ImportError:
    pass
