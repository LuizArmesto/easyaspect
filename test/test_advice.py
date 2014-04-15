import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from easyaspect.advice import _Advice, before, after, around


class Test_Advice(unittest.TestCase):
    def test_properties(self):

        def func():
            pass

        advice = _Advice('type', 'pointcut', 'target', func)
        self.assertEqual('type', advice.type)
        self.assertEqual('pointcut', advice.pointcut)
        self.assertEqual('target', advice.target)
        self.assertEqual(func, advice.func)
        self.assertEqual('func', advice.name)

    def test_callable(self):
        mocked = mock.Mock(['__name__'])
        advice = _Advice('', '', '', mocked)
        advice('arg')
        mocked.assert_called_once_with('arg')


class TestDecorators(unittest.TestCase):
    def test_advice_attribute(self):

        def func():
            pass

        self.assertRaises(AttributeError, getattr, func, '_advices')
        wrapped = before(['DummyClass.*'], target='_target')(func)
        self.assertTrue(isinstance(getattr(wrapped, '_advices'), list))
        self.assertEqual(1, len(wrapped._advices))

    def test_before(self):

        def func():
            pass

        wrapped = before(['DummyClass.*'], target='_target')(func)
        self.assertEqual('before', wrapped._advices[0].type)
        self.assertEqual('_target', wrapped._advices[0].target)
        self.assertEqual(func, wrapped._advices[0].func)

    def test_after(self):

        def func():
            pass

        wrapped = after(['DummyClass.*'], target='_target')(func)
        self.assertEqual('after', wrapped._advices[0].type)
        self.assertEqual('_target', wrapped._advices[0].target)
        self.assertEqual(func, wrapped._advices[0].func)

    def test_around(self):

        def func():
            pass

        wrapped = around(['DummyClass.*'], target='_spam')(func)
        self.assertEqual('around', wrapped._advices[0].type)
        self.assertEqual('_spam', wrapped._advices[0].target)
        self.assertEqual(func, wrapped._advices[0].func)
