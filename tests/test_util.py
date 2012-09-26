import tw2.core as twc
from thread import start_new_thread
from Queue import Queue


class TestRequestLocal:

    def test_for_each_thread_uses_different_dict(self):
        queue = Queue()
        put_request_local_in_shared_queue = lambda: queue.put(twc.util.thread_local())

        start_new_thread(put_request_local_in_shared_queue, ())

        assert queue.get() is not twc.util.thread_local(), (
            'Expected anything except %r but got it' % twc.util.thread_local())
