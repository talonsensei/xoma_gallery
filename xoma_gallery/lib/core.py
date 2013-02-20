'''
Houses functions that should be built into Python but are not.
'''

def nested_property(fn):
    '''
    This is meant to be a decorator for property functions. Using @property as a
    decorator will only work for read-only properties. This method assumes that 
    the function being decorated uses the common property idiom:
    
    def my_property():
        doc = 'doc for my property'
        def fget(self): 
            return return self._my_property
        def fset(self, val):
            self._my_property = val
        def fdel(self):
            del(self._my_property)
        return locals()
    
    Note: that you can also use a docstring on the my_property() function and it
    will set that as the doc for the property.
    '''
    prop_fns = fn()
    if 'doc' not in prop_fns:
        prop_fns['doc'] = fn.__doc__
    return property(**prop_fns)