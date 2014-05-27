class AccessDict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except:
            return None

    @classmethod
    def prepare(cls, di):
        """
        Takes a normal dict and returns an AccessDict
        with all nested dicts also converted to AccessDicts
        """
        di = cls(di)
        for key, value in di.iteritems():
            if type(value) == dict:
                di[key] = cls.prepare(value)
        return di
