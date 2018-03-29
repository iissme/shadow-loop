import asyncio
import threading
import weakref
import concurrent.futures
import logging

from functools import partial
from threading import Thread


log = logging.getLogger(__name__)


class ShadowLoop:
    def __init__(self, debug=False):
        self.loop = asyncio.new_event_loop()
        self.loop.set_debug(debug)
        self.loop_thread = Thread(daemon=True,
                                  target=self._start_shadow_loop,
                                  name='ShadowLoopThread')
        self.loop_thread.start()
        self._finalizer = weakref.finalize(self, self.stop)

    def _start_shadow_loop(self):
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_forever()
        except Exception as e:
            log.error('Shadow loop has exited with:\n', exc_info=e)
            self.loop.close()

    # Note that you can't `await` this Futures/Tasks directly from another thread!
    # Use `await_for` for this if needed.
    def create_task(self, task):
        def wrapper(other_thread_future, t):
            pending_task = asyncio.Task(t, loop=self.loop)
            pending_task.add_done_callback(self.future_task_done)
            other_thread_future.set_result(pending_task)

        done_future = concurrent.futures.Future()
        self.loop.call_soon_threadsafe(partial(wrapper, done_future, task))
        return done_future.result()

    def create_future(self):
        def wrapper(other_thread_future):
            pending_future = asyncio.Future(loop=self.loop)
            pending_future.add_done_callback(self.future_task_done)
            other_thread_future.set_result(pending_future)

        done_future = concurrent.futures.Future()
        self.loop.call_soon_threadsafe(partial(wrapper, done_future))
        return done_future.result()

    @staticmethod
    def future_task_done(future):
        try:
            future.result()
        except Exception as e:
            trace = getattr(future, '_source_traceback', None)
            full_trace = ''.join(trace.format()) if trace else 'Not available.'
            log.warning(f'Shadow loop task/future got exception!\n'
                        f'Full traceback:\n{full_trace}\nExc info:\n', exc_info=e)

    def _safe_run(self, cb, *args, **kwargs):
        return self.loop.call_soon_threadsafe(partial(cb, *args, **kwargs))

    def _submit(self, awaitable):
        """
        Similar to `run_coroutine_threadsafe` but accepts awaitable. Returns concurrent.futures.Future
        which is done when coro submitted to shadow loop finished with result or exception.
        """
        future = concurrent.futures.Future()

        def callback():
            try:
                asyncio.futures._chain_future(asyncio.ensure_future(awaitable, loop=self.loop), future)
            except Exception as exc:
                if future.set_running_or_notify_cancel():
                    future.set_exception(exc)
                raise

        self.loop.call_soon_threadsafe(callback)
        return future

    def await_for(self, awaitable):
        return self._submit(awaitable).result()

    def stop(self, wait=True):
        for task in asyncio.Task.all_tasks(loop=self.loop):
            log.warning(f'Cancelling {task}...\n')
            self._safe_run(task.cancel)

        self._safe_run(self.loop.stop)
        if wait:
            self.loop_thread.join()
