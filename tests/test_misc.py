import tw2.core as twc, testapi

try:
    import thread
except ImportError:
    import _thread as thread


class TestMisc(object):
    def setUp(self):
        testapi.setup()

    def test_request_local(self):
        twc.util._thread_local = {}
        rl = twc.util.thread_local()
        thread.start_new_thread(self._rl_thread2, (rl,))
    def _rl_thread2(self, rl):
        assert(twc.util.thread_local() is not rl)
