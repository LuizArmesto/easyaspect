import fnmatch
from importlib import import_module
from inspect import ismethod, isclass, ismodule, currentframe

__all__ = ['get_module', 'get_classes', 'get_properties', 'get_methods']


def get_module(module_name):
    """Imports and returns a module."""
    if not module_name:
        return None
    return import_module(module_name)


def get_classes(module, pattern=None):
    """Returns a list of classes defined in `module` that match `pattern`.

    The argument `module` can be a string, a module object (see get_module)
    or a dictionary, like the one returned by `globals()` for example.
    The argument `pattern` should be a string that can contain wildcards.
    """
    if isclass(module):
        return [module]
    elif not pattern and isinstance(module, basestring):
        if '.' in module:
            return get_classes(*module.rsplit('.', 1))
        else:
            classes = []
            pattern = module
            # Got only the class and the method names
            # Lets inspect the execution frame stack to get the class
            # reference
            frame_ = currentframe()
            try:
                # Go back frames in execution stack to reach this class
                # initialization and try to find the reference to the class
                # we are looking for.
                frame = frame_
                while frame:
                    classes += get_classes(frame.f_globals, pattern)
                    frame = getattr(frame, 'f_back', None)
            finally:
                # Avoid leaks
                del frame_
                del frame
            return list(set(classes))  # Remove duplicates
    if isinstance(module, basestring):
        return get_classes(get_module(module), pattern)
    # Get the classes from a module
    elif ismodule(module):
        attrs = (getattr(module, n)
                 for n in fnmatch.filter(dir(module), pattern))
    # Get the classes from a dictionary
    elif isinstance(module, dict):
        attrs = (module[n] for n in fnmatch.filter(module.keys(), pattern))
    else:
        raise TypeError(
            '\'get_classes\' requires a string, a module object or a '
            'dictionary as first argument but got {}'.format(type(module)))
    return [attr for attr in attrs if isclass(attr)]


def get_properties(cls, pattern=None):
    """Returns a list of `cls` properties that match `pattern`.

    The argument `pattern` should be a string that can contain wildcards.
    """
    return get_members(cls, pattern, lambda a: not ismethod(a))


def get_methods(cls, pattern=None):
    """Returns a list of `cls` methods that match `pattern`.

    The argument `pattern` should be a string that can contain wildcards.
    """
    if ismethod(cls):
        return [(cls.im_class, [(cls.__name__, cls)])]
    return get_members(cls, pattern, ismethod)


def get_members(cls, pattern=None, filter_func=lambda a: True):
    """Returns a list of `cls` members that match `pattern`.

    The argument `pattern` should be a string that can contain wildcards.
    """
    if not pattern and isinstance(cls, basestring):
        cls, pattern = cls.rsplit('.', 1)
        return get_members(cls, pattern, filter_func)
    elif isclass(cls) or isinstance(cls, basestring):
        return [(cls_, [(name, getattr(cls_, name))
                        for name in fnmatch.filter(dir(cls_), pattern)
                        if filter_func(getattr(cls_, name))])
                for cls_ in get_classes(cls)]
    else:
        return []
