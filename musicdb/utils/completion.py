import readline

class BaseCompleter(object):
    def install(self):
        readline.set_completer(self)
        readline.parse_and_bind('tab: complete')
        readline.set_completer_delims('')

class QuerySetCompleter(BaseCompleter):
    """
    import readline
    from mymodels import Model

    completer = QuerySetCompleter(Model.objects.all(), 'name')

    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)
    readline.set_completer_delims('')

    while 1:
        print repr(raw_input(">>> "))
    """

    def __init__(self, qs, field):
        self.qs = qs
        self.field = field

        self.prefix = None

    def __call__(self, prefix, index):
        # New prefix
        if prefix != self.prefix:
            qs = self.qs.values_list(self.field, flat=True)

            if prefix:
                qs = qs.filter(**{
                    '%s__startswith' % self.field: prefix,
                })

            self.matching = list(qs)
            self.prefix = prefix

        try:
            return self.matching[index]
        except IndexError:
            return None

class Completer(BaseCompleter):
    """
    import readline

    completer = QuerySetCompleter(iterable)

    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)
    readline.set_completer_delims('')

    while 1:
        print repr(raw_input(">>> "))
    """

    def __init__(self, iterable):
        self.data = list(iterable)
        self.prefix = None

    def __call__(self, prefix, index):
        # New prefix
        if prefix != self.prefix:
            self.matching = [
                x for x in self.data if x.startswith(prefix)
            ]
            self.prefix = prefix

        try:
            return self.matching[index]
        except IndexError:
            return None
