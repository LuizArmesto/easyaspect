import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from easyaspect.pointcut import Pointcut, get_original, reset
from easyaspect.advice import _Advice


class TestFunctions(unittest.TestCase):
    def test_get_original(self):
        pointcut = Pointcut()

        def func():
            pass

        wrapped = pointcut.wrap(func)
        self.assertNotEqual(func, wrapped)
        orig = get_original(wrapped)
        self.assertEqual(func, orig)


class DummyClass:
    prop = 42
    def method(self, a, b):
        return a + b


class TestPointcut(unittest.TestCase):
    def setUp(self):
        self.orig_method = DummyClass.method
        self.orig_prop = DummyClass.prop

    def tearDown(self):
        DummyClass.method = self.orig_method
        DummyClass.prop =  self.orig_prop

    def test_joinpoints_wrapping_method(self):
        self.assertEqual(DummyClass.method, self.orig_method)
        self.assertTrue(isinstance(DummyClass.prop, int))
        Pointcut(['DummyClass.*'], target='methods')
        self.assertNotEqual(DummyClass.method, self.orig_method)
        self.assertTrue(isinstance(DummyClass.prop, int))

    def test_joinpoints_wrapping_method_twice(self):
        pointcut = Pointcut(['DummyClass.*'])

        def func():
            pass

        wrapped = pointcut.wrap(func)
        rewrapped = pointcut.wrap(wrapped)
        # Should not wrap again
        self.assertEqual(wrapped, rewrapped)

    def test_joinpoints_wrapping_properties(self):
        self.assertEqual(DummyClass.method, self.orig_method)
        self.assertTrue(isinstance(DummyClass.prop, int))
        Pointcut(['DummyClass.*'], target='properties')
        self.assertEqual(DummyClass.method, self.orig_method)
        self.assertTrue(isinstance(DummyClass.prop, property))

    def test_get_advices(self):
        pointcut = Pointcut(['DummyClass.*'])
        a1 = _Advice('before', pointcut, 'all', DummyClass.method)
        a2 = _Advice('before', pointcut, 'all', DummyClass.method)
        a3 = _Advice('after', pointcut, 'all', DummyClass.method)
        a4 = _Advice('around', pointcut, 'all', lambda a: a)
        pointcut.add_advice(a1)
        pointcut.add_advice(a2)
        pointcut.add_advice(a3)
        pointcut.add_advice(a4)

        self.assertEqual({'after': [a3], 'before': [a1, a2], 'around': [a4]},
                         pointcut.advices)

    def test_disable_enable(self):
        pointcut = Pointcut(['DummyClass.*'])
        a1 = _Advice('before', pointcut, 'all', DummyClass.method)
        a2 = _Advice('around', pointcut, 'all', lambda a: a)
        pointcut.add_advice(a1)
        pointcut.add_advice(a2)
        pointcut.disable()
        self.assertEqual({'after': [], 'before': [], 'around': []},
                         pointcut.advices)
        pointcut.enable()
        self.assertEqual({'after': [], 'before': [a1], 'around': [a2]},
                         pointcut.advices)

    def test_disable_specific_advice(self):
        pointcut = Pointcut(['DummyClass.*'])
        a1 = _Advice('before', pointcut, 'all', DummyClass.method)
        a2 = _Advice('around', pointcut, 'all', lambda a: a)
        pointcut.add_advice(a1)
        pointcut.add_advice(a2)
        pointcut.disable('method')
        self.assertEqual({'after': [], 'before': [], 'around': [a2]},
                         pointcut.advices)
        pointcut.enable()
        self.assertEqual({'after': [], 'before': [a1], 'around': [a2]},
                         pointcut.advices)

    def test_reset_string(self):
        self.assertEqual(DummyClass.method, self.orig_method)
        Pointcut(['DummyClass.*'])
        self.assertNotEqual(DummyClass.method, self.orig_method)
        reset('DummyClass.*')
        self.assertEqual(DummyClass.method, self.orig_method)

    def test_reset_method(self):
        self.assertEqual(DummyClass.method, self.orig_method)
        Pointcut(['DummyClass.*'], target='methods')
        self.assertNotEqual(DummyClass.method, self.orig_method)
        reset(DummyClass.method)
        self.assertEqual(DummyClass.method, self.orig_method)
