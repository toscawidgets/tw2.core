import testapi
import tw2.core as twc


class TestI18N(object):
    def setUp(self):
        testapi.setup()

    def test_get_translator(self):
        # Test that get_translator() doesn't throw an exception.
        twc.i18n.get_translator()
