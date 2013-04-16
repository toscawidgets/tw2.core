from unittest import TestCase
from tw2.core.mako_util import attrs
import six

fake_context = None

class TestMakoUtil(TestCase):
    def test_normal_attrs(self):
        s = attrs(fake_context, attrs={'a':5, 'b':3})
        self.failUnless(s == six.u('a="5" b="3"') or s == six.u('b="3" a="5"'))

    def test_normal_attrs_as_args(self):
        s = attrs(fake_context, {'a':5, 'b':3})
        self.failUnless(s == six.u('a="5" b="3"') or s == six.u('b="3" a="5"'))

    def test_boolean_attrs(self):
        s = attrs(fake_context, attrs={'a':True, 'b':False})
        self.failUnless(s == six.u('a="True" b="False"') or s == six.u('b="False" a="True"'))

    def test_none_attrs(self):
        """Attributes with None values are not rendered"""
        s = attrs(fake_context, attrs={'a':'hello', 'b':None})
        self.assertEqual(s, six.u('a="hello"'))

    def test_special_boolean_html_attrs(self):
        s = attrs(fake_context, attrs={'checked':True})
        self.assertEqual(s, six.u('checked="checked"'))

        s = attrs(fake_context, attrs={'checked':False})
        self.assertEqual(s, six.u(''))

        s = attrs(fake_context, attrs={'checked':None})
        self.assertEqual(s, six.u(''))
