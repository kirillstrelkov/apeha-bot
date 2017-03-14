class Property(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return u"%s: %s" % (self.name, self.value)
