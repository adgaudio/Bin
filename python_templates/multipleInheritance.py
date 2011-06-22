class D(dict, object):
    """A combination of dict and object
    Lets you add namespace vars to a dictionary and vice versa

    Interesting: you can create namespace variables that are integers
    """
    def __additems__(self):
        """add namespace vars to dict"""
        self.update(**self.__dict__)
    def __addvars__(self):
        """add dict items into namespace"""
        self.__dict__.update(self.items())


d = D()
d.x = 'a'
print d.x
d.update(b='dude')
d[5]=8
d.__additems__()
print d
