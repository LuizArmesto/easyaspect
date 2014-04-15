# TODO: create a prefix to be used by all attributes injected into functions
import fnmatch
from collections import defaultdict, Iterable
from functools import wraps
from inspect import ismethod

from .utils import get_members, get_methods, get_properties

__all__ = ['Pointcut', 'reset', 'get_original']

ALL = 'all'
PROPERTIES = 'properties'
METHODS = 'methods'

DEFAULT_TARGET = ALL

INTERNAL_PROPS = []


class Pointcut(object):
    def __init__(self, joinpoints=[], target=DEFAULT_TARGET):
        self.name = None
        self.target = target or DEFAULT_TARGET
        self.__advices = defaultdict(list)
        self.enable()
        # The class accepts one joinpoint without a list, but works only with
        # a list of joinpoints
        if not isinstance(joinpoints, Iterable) or isinstance(
                joinpoints, basestring):
            joinpoints = [joinpoints]
        for joinpoint in joinpoints:
            self._handle_joinpoint(joinpoint)

    def get_advices(self):
        """Returns the enabled advices."""
        if not self.enabled:
            return {'before': [], 'around': [], 'after': []}
        return {
            'before': [advice for advice in self.__advices['before'] if
                       not advice.name in self._disabled_advices],
            'around': [advice for advice in self.__advices['around'] if
                       not advice.name in self._disabled_advices],
            'after': [advice for advice in self.__advices['after'] if
                      not advice.name in self._disabled_advices]
        }

    advices = property(get_advices)

    def add_advice(self, advice):
        """Adds an advice associated with some joinpoint of this pointcut."""
        if not advice in self.__advices[advice.type]:
            self.__advices[advice.type].append(advice)

    def enable(self):
        self._disabled_advices = []
        self.enabled = True

    def disable(self, advice_name=None):
        if advice_name:
            self._disabled_advices.append(advice_name)
        else:
            # TODO: disable all advices instead of disable the pointcut itself
            self.enabled = False

    def _handle_joinpoint(self, joinpoint):
        # Handle methods
        if self.target in (ALL, METHODS):
            for cls, funcs in get_methods(joinpoint):
                for name, func in funcs:
                    # Replace the original function with the wrapped version
                    setattr(cls, name, self.wrap(func, name))
        # Handle properties
        if self.target in (ALL, PROPERTIES):
            for cls, props in get_properties(joinpoint):
                for name, prop in props:
                    # Ignore internal properties
                    if (not fnmatch.fnmatch(name, '__*__') and
                            not name.startswith('__advised_prop_') and
                            not name in INTERNAL_PROPS):
                        # Create `property` object if needed
                        if not isinstance(prop, property):
                            advised_prop_name = '__advised_prop_{}'.format(
                                name)
                            setattr(cls, advised_prop_name, prop)

                            # Using a factory function to set the correct name
                            def create_prop(name):
                                return property(
                                    lambda self: getattr(self, name),
                                    lambda self, value:
                                    setattr(self, name, value))
                            prop = create_prop(advised_prop_name)
                            setattr(cls, name, prop)
                        # Create a new property using the wrapped setter
                        # function
                        prop = prop.setter(self.wrap(prop.fset, name))
                        setattr(cls, name, prop)

    def wrap(self, func, name=None):
        """Wraps the original function to run advices."""
        name = name or func.__name__
        cls = getattr(func, 'im_class', None)
        # Avoid to wrap an already wrapped function
        if hasattr(func, '_orig_func'):
            advised_func = func
        else:
            _pointcuts = []  # We use the fact that lists are mutable

            @wraps(func)
            def advised_func(*args, **kwargs):
                pointcuts = []
                obj = args[0]

                # Get pointcuts from parent classes only if the class doesn't
                # overrided the method
                cls = type(obj)
                if hasattr(getattr(cls, name), '_created_by_aspect'):
                    for cls in type.mro(type(obj))[1:]:
                        if not hasattr(getattr(cls, name),
                                       '_created_by_aspect'):
                            parent_cls_func = getattr(cls, name, None)
                            if isinstance(parent_cls_func, property):
                                parent_cls_func = parent_cls_func.fset
                            if parent_cls_func and hasattr(
                                    parent_cls_func, '_pointcuts'):
                                pointcuts += parent_cls_func._pointcuts
                            break
                pointcuts += _pointcuts

                # Create function to be passed to 'around' advice
                def create_advised_func(func_, next_):
                    def _func(*args, **kwargs):
                        return func_(pointcut.aspect, name, next_,
                                     *args, **kwargs)
                    return _func

                # Wrap the original function with 'before' and 'after'
                # advices
                def advised(*args, **kwargs):
                    # Execute 'before' advices
                    for pointcut in pointcuts:
                        for before in pointcut.advices['before']:
                            before(pointcut.aspect, name, *args, **kwargs)
                    ret = func(*args, **kwargs)
                    # Execute 'after' advices
                    for pointcut in pointcuts:
                        for after in pointcut.advices['after']:
                            after(pointcut.aspect, name, *args, **kwargs)
                    return ret

                # Execute 'around' advices
                for pointcut in pointcuts:
                    for advice in pointcut.advices['around']:
                        advised = create_advised_func(advice, advised)
                ret = advised(*args, **kwargs)
                return ret

            # Save reference to original function
            advised_func._orig_func = func
            # Save reference to point cuts list
            advised_func._pointcuts = _pointcuts
        # This is the same `_pointcuts` list defined above
        advised_func._pointcuts.append(self)
        if cls and not name in vars(cls):
            advised_func._created_by_aspect = True
        return advised_func


def get_original(function):
    while function:
        orig_func = function
        if isinstance(function, property):
            fset = getattr(function.fset, '_orig_func', None)
            if fset:
                return function.setter(fset)
        else:
            function = getattr(function, '_orig_func', None)
    return orig_func


def reset(joinpoint, cls=None, name=None):
    if ismethod(joinpoint):
        setattr(cls or joinpoint.im_class, name or joinpoint.__name__,
                get_original(joinpoint))
    elif isinstance(joinpoint, property):
        setattr(cls, name, get_original(joinpoint))
    elif isinstance(joinpoint, basestring):
        for cls, members in get_members(joinpoint):
            for name, member in members:
                reset(member, cls, name)
