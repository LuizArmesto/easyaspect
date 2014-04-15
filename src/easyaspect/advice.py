# There will be one decorator for each item in this list
ADVICE_TYPES = ['before', 'after', 'around']


class _Advice(object):
    """Internal class for defining advices.

    To define advices use the advice decorators with `Aspect` class methods.
    """
    def __init__(self, type, pointcut, target, func):
        self.type = type
        self.pointcut = pointcut
        self.target = target
        self.func = func
        self.name = func.__name__

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def _make_advice_decorator(advice_type):
    """Makes new advice decorators to be used within `Aspect` subclasses."""
    def advice_decorator(pointcut, target=None):
        # `pointcut` can be a `Pointcut` object, a string containing the name
        # of the `Aspect` class attribute containing a `Pointcut` object or
        # a string or a list of strings containing joinpoints.
        # The value of `pointcut` is handled by `_AspectMetaClass.__new__`.
        def wrapper(func):
            # Make sure the `_advices` attribute exists
            func._advices = getattr(func, '_advices', [])
            # Add the current advice to the list of advices
            func._advices.append(
                _Advice(advice_type, pointcut, target, func))
            # Return the function itself
            return func
        return wrapper
    # Rename the decorator function to use the advice type as name
    advice_decorator.__name__ = advice_type
    return advice_decorator

# Create dynamically all advice decorators
for advice_type in ADVICE_TYPES:
    decorator = _make_advice_decorator(advice_type)
    exec '{} = decorator'.format(advice_type)

# Export only the decorators
__all__ = ADVICE_TYPES
