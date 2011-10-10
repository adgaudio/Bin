"""Simple utils to make working with Mixins and dynamic inheritance easier"""


def _return(f, args, kwargs):
    """Helper function returns instance if args or object"""
    if args or kwargs:
        return f(*args, **kwargs)
    else:
        return f

def make(cls, mixin, *args, **kwargs):
    """Add mixin to cls
    Return instance if args or kwargs, else return class obj"""
    return makes(cls, (mixin,), *args, **kwargs)

def makes(cls, mixins, *args, **kwargs):
    """Return new class inheriting from cls and tuple of mixins.
    Return an instance if params"""
    parents = [cls] + [x for x in mixins]

    class NewClass(cls): pass
    NewClass.__bases__ += tuple(mixins)
    NewClass.__name__ += "_WithMixins"
    return _return(NewClass, args, kwargs)

def imake(inst, mixin):
    """Return new instance
    that inherits from given class instance and mixin class
    assume inst.__init__(inst) will work"""
    return makes(inst.__class__, (mixin,), inst)


if __name__ == '__main__':

    def doctests():
        """
        >>> class Car(object):
        ...     def carmethod(self):
        ...         return 'from car:', self
        >>> class Truck(object):
        ...     def truckmethod(self):
        ...         return 'from truck:', self

        >>> a = makes(list, [Car, Truck], ['input', 'data'])
        >>> a.append(1)
        >>> a.carmethod()
        ('from car:', ['input', 'data', 1])
        >>> a.truckmethod()
        ('from truck:', ['input', 'data', 1])
        >>>

        >>> b = imake([1,2,3], Car)
        >>> b.append('a')
        >>> b.carmethod()
        ('from car:', [1, 2, 3, 'a'])
        """

    print "Running doctests"
    import doctest
    print doctest.testmod()
