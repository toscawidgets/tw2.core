# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from nose.tools import eq_

import testapi

import tw2.core as twc


def _(x): return x


class TestI18N(object):
    def setUp(self):
        testapi.setup()

    def test_get_translator(self):
        # Test that get_translator() doesn't throw an exception.
        twc.i18n.get_translator()

    def test_primary_translation(self):
        # Test that the best possible translation is used.
        translator = twc.i18n.get_translator(lang=('de', 'en'))
        eq_(translator(_("Must be a valid URL")),
            "Bitte eine gültige URL eingeben")

    def test_skip_unknown_language(self):
        # Test that languages without a corresponding message catalog are
        # skipped.
        translator = twc.i18n.get_translator(lang=('nolanguage', 'de', 'en'))
        eq_(translator(_("Must be a valid URL")),
            "Bitte eine gültige URL eingeben")
