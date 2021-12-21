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
