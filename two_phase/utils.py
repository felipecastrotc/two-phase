# Check if a variable is iterable or not
def iterable(obj):
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return True


# Return kwargs from a list of variables and keys
def zip_dict(vars, keys):
    for v in zip(*vars):
        yield {key: i for key, i in zip(keys, v)}


def get_iter(kwargs):
    # List of variables and keys that are an iterable
    var, keys = [], []
    # Check which variable is an iterable
    for key in kwargs.keys():
        if iterable(kwargs[key]):
            var += [kwargs[key]]
            keys += [key]
    return var, keys


def get_kwargs(kwargs):
    # Check which var is iterable
    var, keys = get_iter(kwargs)
    # Check to return the kwargs as it is or as an iterator
    if len(keys) > 0:
        # Remove the variables that is not iterable
        for k in keys:
            kwargs.pop(k, None)
        #  Iterate over the values
        for dct in zip_dict(var, keys):
            kwargs.update(dct)
            yield kwargs
    else:
        yield kwargs
