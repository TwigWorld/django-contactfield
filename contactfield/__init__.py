from django.conf import settings
if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^contactfield\.fields\.(ContactField)"])
