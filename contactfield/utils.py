class CastOnAssign(object):
    """
    An object which ensures that `field.to_python()` is called on assignment to the
    field. This behaviour used to be provided by the
    `django.db.models.subclassing.Creator` class that was removed in Django 1.10
    """

    def __init__(self, field):
        self.field = field

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return obj.__dict__[self.field.name]

    def __set__(self, obj, value):
        obj.__dict__[self.field.name] = self.field.to_python(value)


class AccessDict(dict):
    def __init__(self, *args, **kwargs):
        super(AccessDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    @classmethod
    def prepare(cls, di):
        """
        Takes a normal dict and returns an AccessDict
        with all nested dicts also converted to AccessDicts
        """
        di = cls(di)
        for key, value in di.items():
            if type(value) == dict:
                di[key] = cls.prepare(value)
        return di
