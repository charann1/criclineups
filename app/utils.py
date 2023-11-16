def get_attrs(obj):
    return [
        getattr(obj, a) for a in dir(obj) if not
        a.startswith('__') and not callable(getattr(obj, a))
    ]
