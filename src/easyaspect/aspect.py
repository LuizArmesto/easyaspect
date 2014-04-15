from collections import defaultdict

from .pointcut import Pointcut

__all__ = ['Aspect']


class _AspectMetaClass(type):
    """Metaclass for defining Aspect.

    This metaclass is used internally only. To create a class to define an
    aspect use the `Aspect` class.
    """
    def __new__(mcls, name, bases, attrs):
        advices = defaultdict(list)
        cls = super(_AspectMetaClass, mcls).__new__(mcls, name, bases, attrs)
        cls._pointcuts = []
        pointcuts = []
        # Go over attributes and look for pointcuts and advices
        for name, value in attrs.iteritems():
            # Get the named pointcuts
            if hasattr(value, 'add_advice'):
                pointcut = value
                pointcut.name = name
                pointcut.aspect = cls
                pointcuts.append(pointcut)
            # The `_advices` attribute is set by decorators from `advice`
            # module. If the attribute has this attribute this means that
            # the current attribute is a method related to an advice
            if hasattr(value, '_advices'):
                for advice in value._advices:
                    advice.aspect = cls
                    # Check if we have the pointcut object itself, the name of
                    # the class attribute containing the pointcut or a
                    # joinpoint list
                    if (isinstance(advice.pointcut, basestring) and
                            advice.pointcut in attrs):
                        # It is a pointcut name, created by some code like
                        #
                        # class C(Aspect):
                        #     pointcut_name = Pointcut('module.Class.method')
                        #     @before('pointcut_name')
                        #     def f(cls, joinpoint, obj, *args, **kwargs):
                        #         ...
                        pointcut_name = advice.pointcut
                    elif not hasattr(advice.pointcut, 'add_advice'):
                        # Probably a joinpoint, created by some code like
                        #
                        # class C(Aspect):
                        #     @before('pkg.module.Class.method')
                        #     def f(cls, joinpoint, obj, *args, **kwargs):
                        #         ...
                        joinpoint = advice.pointcut
                        # Lets create a new pointcut using it
                        advice.pointcut = Pointcut(joinpoint, advice.target)
                        pointcut_name = advice.pointcut.name
                    # Treat the pointcut object, setting some values and making
                    # some associations
                    if hasattr(advice.pointcut, 'add_advice'):
                        cls._pointcuts.append(advice.pointcut)
                        # The decorator got a pointcut directly
                        pointcut_name = advice.pointcut.name
                        if not advice.pointcut.name:
                            # It is an annonymous pointcut, created by some
                            # code like
                            #
                            # class C(Aspect):
                            #     @before(Pointcut('pkg.module.Class.method'))
                            #     def f(cls, joinpoint, obj, *args, **kwargs):
                            #         ...
                            #
                            # or a reference to a named pointcut not handled
                            # yet, created by some code like
                            #
                            # class C(Aspect):
                            #     pointcut_name = Pointcut('Class.method')
                            #     @before(pointcut_name)
                            #     def f(cls, joinpoint, obj, *args, **kwargs):
                            #         ...
                            advice.pointcut.add_advice(advice)
                            advice.pointcut.aspect = cls
                    advices[pointcut_name].append(advice)
        # Associate the named pointcuts with its advices
        for pointcut in pointcuts:
            if not pointcut in cls._pointcuts:
                cls._pointcuts.append(pointcut)
            for advice in advices.get(pointcut.name, []):
                pointcut.add_advice(advice)
        return cls


class Aspect(object):
    """Class for defining aspects.

    Subclass this class to create an Aspect. The Aspect classes are abstract
    and can't be instatiated.

    Usage:

        class AspectName(Aspect):
            pointcut_name = Pointcut('pkg.module.Class.method')

            @before('pointcut_name')
            def before_pointcut_name(cls, joinpoint, obj, *args, **kwargs):
                ...

    """
    __metaclass__ = _AspectMetaClass

    @classmethod
    def enable(cls, *args, **kwargs):
        for pointcut in cls._pointcuts:
            pointcut.enable(*args, **kwargs)

    @classmethod
    def disable(cls, *args, **kwargs):
        for pointcut in cls._pointcuts:
            pointcut.disable(*args, **kwargs)
