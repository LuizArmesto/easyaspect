import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from easyaspect import Aspect, Pointcut, before


class TestAspect(unittest.TestCase):
    def test_named_pointcuts(self):

        class DummyAspect(Aspect):
            named_pointcut = Pointcut('DummyClass.*')

            @before(named_pointcut)
            def advice_func(self):
                pass

        self.assertEqual([DummyAspect.named_pointcut],
                         DummyAspect._pointcuts)

    def test_named_pointcuts_with_string(self):

        class DummyAspect(Aspect):
            named_pointcut = Pointcut('DummyClass.*')

            @before('named_pointcut')
            def advice_func(self):
                pass

        self.assertEqual([DummyAspect.named_pointcut],
                         DummyAspect._pointcuts)

    @mock.patch('easyaspect.aspect.Pointcut')
    def test_string_pointcuts(self, MockedPointcut):

        class DummyAspect(Aspect):
            @before('DummyClass.*', target='__targ')
            def advice_func(self):
                pass

        self.assertEqual(1, len(DummyAspect._pointcuts))
        MockedPointcut.assert_called_with('DummyClass.*', '__targ')

    @mock.patch('easyaspect.aspect.Pointcut')
    def test_list_of_strings_pointcuts(self, MockedPointcut):

        class DummyAspect(Aspect):
            @before(['DummyClass.*', 'Dummy*.*'], target='__targ')
            def advice_func(self):
                pass

        self.assertEqual(1, len(DummyAspect._pointcuts))
        MockedPointcut.assert_called_with(['DummyClass.*', 'Dummy*.*'],
                                          '__targ')

    def test_disable(self):

        class DummyAspect(Aspect):
            named_pointcut = mock.Mock(Pointcut('DummyClass.*'))

            @before(named_pointcut)
            def advice_func(self):
                pass

        DummyAspect.disable('arg')
        DummyAspect.named_pointcut.disable.assert_called_once_with('arg')

    def test_enable(self):

        class DummyAspect(Aspect):
            named_pointcut = mock.Mock(Pointcut('DummyClass.*'))
            another_pointcut = mock.Mock(Pointcut('Dummy*.*'))

            @before(named_pointcut)
            def advice_func(self):
                pass

        DummyAspect.enable('spam')
        DummyAspect.named_pointcut.enable.assert_called_once_with('spam')
        DummyAspect.another_pointcut.enable.assert_called_once_with('spam')
