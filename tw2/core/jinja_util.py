from copy import copy

_BOOLEAN_ATTRS = frozenset(['selected', 'checked', 'compact', 'declare',
                            'defer', 'disabled', 'ismap', 'multiple',
                            'nohref', 'noresize', 'noshade', 'nowrap'])

def htmlbools(v):
    attrs = copy(v)
    for key in filter(lambda k: k in _BOOLEAN_ATTRS and attrs[k], attrs.keys()):
        attrs[key] = key
    return attrs
