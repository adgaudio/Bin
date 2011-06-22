class using(object):
    def __init__(self, obj):
        self._wrappee = obj

    def unwrap(self):
        return self._wrappee

    def __getattr__(self, attr, *a, **b):
        def wrapper(*args, **kwargs):
            """Returns self after 
            sending given parameters to previously given attribute"""
            getattr(self._wrappee, attr)(*args, **kwargs)
            return self
        return wrapper
        

print("Example: this class allows you to update a bunch of times in a row")
d = dict()
print using(d).update(dict(a=1)).update(dict(b=2)).unwrap()
# prints {'a': 1, 'b': 2}
l = list()
print using(l).append(1).append(2).unwrap() 
#...you can't do these with a normal dict
