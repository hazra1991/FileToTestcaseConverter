import six

def dot_splitter(flat_key):
    keys = tuple(flat_key.split("."))
    return keys

SPLITTER_DICT = {
    "dot": dot_splitter
}

def nested_set_dict(d, keys, value):

    """Set a value to a sequence of nested keys only works on dics that have key as a non numeric string or type

    Parameters
    ----------
    d : Mapping
    keys : Sequence[str]
    value : Any
    """
    assert keys
    key = keys[0]
    if len(keys) == 1:
        if type(d) == list:
            d.append(value)
        else:
            d[key] = value
        return

    # convert to int if it is a string digit
    if isinstance(keys[1], str) and keys[1].isdigit():
        keys[1] = int(keys[1])

    # the type is a string so make a dict if none exists
    if type(keys[1]) == int:
        if key in d:
            pass
        elif type(d) == list and type(key) == int:
            if not d:
                d.append([])
            if key == len(d):
                d.append([])
        else:
            d[key] = []
        d = d[key]
    elif type(key) == int:
        if (key + 1) > len(d):
            d.append({})
        d = d[key]
    else:
        d = d.setdefault(key, {})
    nested_set_dict(d, keys[1:], value)

def unflatten(d, splitter="dot", inverse=False):
    """Unflatten dict-like object.

    Parameters
    ----------
    d : dict-like object
        The dict that will be unflattened.
    splitter : { 'dot', callable}`

    Returns
    -------
    unflattened_dict : dict
    """
    if isinstance(splitter, str):
        splitter: callable = SPLITTER_DICT[splitter]

    unflattened_dict = {}
    for flat_key, value in six.viewitems(d):
        if inverse:
            flat_key, value = value, flat_key
        key_tuple = list(splitter(flat_key))
        nested_set_dict(unflattened_dict, key_tuple, value)

    return unflattened_dict