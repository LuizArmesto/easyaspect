import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from easyaspect.utils import (get_module, get_classes, get_methods,
                              get_properties)


class DummyClass(object):
    prop_a = 'string'
    prop_b = 42

    def method_a(self):
        pass

    def method_b(self):
        pass


class TestModule(unittest.TestCase):
    def test_empty_module_name(self):
        self.assertEqual(None, get_module(''))

    def test_exception_when_not_found(self):
        self.assertRaises(
            ImportError, get_module, 'this_module_should_not_exist_jdjfkrkd')

    @mock.patch('easyaspect.utils.import_module')
    def test_import_and_return_a_module(self, mocked_import_module):
        mocked_import_module.return_value = 'module_returned'
        self.assertEqual('module_returned', get_module('module_name'))


class TestClasses(unittest.TestCase):
    def test_with_dictionary(self):
        self.assertEqual([DummyClass], get_classes(globals(), 'Dummy*'))

    def test_with_module(self):
        from importlib import import_module
        module = import_module(DummyClass.__module__)
        self.assertEqual([DummyClass], get_classes(module, 'Dummy*'))

    def test_with_string(self):
        module = DummyClass.__module__
        self.assertEqual([DummyClass], get_classes(module, 'Dummy*'))

    def test_with_complete_string(self):
        module = DummyClass.__module__
        self.assertEqual([DummyClass],
                         get_classes('{}.Dummy*'.format(module)))

    def test_with_only_classname_string(self):
        self.assertEqual([DummyClass], get_classes('Dummy*'))

    def test_wrong_cls_type(self):
        self.assertRaises(TypeError, get_classes, 0, 'Dummy*')

    def test_with_class_itself(self):
        self.assertEqual([DummyClass], get_classes(DummyClass))

    def test_not_found(self):
        module = DummyClass.__module__
        self.assertEqual([], get_classes(module, 'Dmmy*'))


class TestMethods(unittest.TestCase):
    def test_get_methods_from_class(self):
        methods = [(DummyClass, [
            ('method_a', DummyClass.method_a),
            ('method_b', DummyClass.method_b)
        ])]
        self.assertEqual(methods, get_methods(DummyClass, 'method_*'))

    def test_get_methods_from_string(self):
        methods = [(DummyClass, [
            ('method_a', DummyClass.method_a),
            ('method_b', DummyClass.method_b)
        ])]
        self.assertEqual(methods, get_methods('DummyClass', 'method_*'))

    def test_get_methods_from_complete_module_string(self):
        methods = [(DummyClass, [
            ('method_a', DummyClass.method_a),
            ('method_b', DummyClass.method_b)
        ])]
        self.assertEqual(methods, get_methods('{}.DummyClass'.format(
            DummyClass.__module__), 'method_*'))

    def test_get_methods_from_full_string(self):
        methods = [(DummyClass, [
            ('method_a', DummyClass.method_a),
            ('method_b', DummyClass.method_b)
        ])]
        self.assertEqual(methods, get_methods('DummyClass.method_*'))

    def test_get_methods_with_wrong_type(self):
        self.assertEqual([], get_methods(0))

    def test_get_methods_from_method_itself(self):
        methods = [(DummyClass, [
            ('method_a', DummyClass.method_a)
        ])]
        self.assertEqual(methods, get_methods(DummyClass.method_a))


class TestProperties(unittest.TestCase):
    def test_get_properties_from_class(self):
        props = [(DummyClass, [
            ('prop_a', DummyClass.prop_a),
            ('prop_b', DummyClass.prop_b)
        ])]
        self.assertEqual(props, get_properties(DummyClass, 'prop_*'))

    def test_get_properties_from_string(self):
        props = [(DummyClass, [
            ('prop_a', DummyClass.prop_a),
            ('prop_b', DummyClass.prop_b)
        ])]
        self.assertEqual(props, get_properties('DummyClass', 'prop_*'))

    def test_get_properties_from_complete_module_string(self):
        props = [(DummyClass, [
            ('prop_a', DummyClass.prop_a),
            ('prop_b', DummyClass.prop_b)
        ])]
        self.assertEqual(props, get_properties('{}.DummyClass'.format(
            DummyClass.__module__), 'prop_*'))

    def test_get_properties_from_full_string(self):
        props = [(DummyClass, [
            ('prop_a', DummyClass.prop_a),
            ('prop_b', DummyClass.prop_b)
        ])]
        self.assertEqual(props,
                         get_properties('{}.DummyClass.prop_*'.format(
                                        DummyClass.__module__)))

    def test_get_properties_with_wrong_type(self):
        self.assertEqual([], get_properties(0))
