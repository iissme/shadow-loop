from .test_asyncio_prepare import *

sl = ShadowLoop(debug=True)


async def shadow_coro():
    await asyncio.sleep(0.1)  # ensure that returning tasks will be pending
    print('Shadow coroutine is done!')
    return True


async def shadow_coro_future(future):
    res = await shadow_coro()
    future.set_result(res)


def test_coro_await():
    assert sl.await_for(shadow_coro()) is True


def test_task_sync():
    task = sl.create_task(shadow_coro())
    assert sl.await_for(task) is True


@async_test
async def test_task_async():
    with pytest.raises(RuntimeError):
        task = sl.create_task(shadow_coro())
        await task  # you can't `await` directly from another thread!


def test_shadow_future():
    shadow_future = sl.create_future()
    sl.create_task(shadow_coro_future(shadow_future))
    assert sl.await_for(shadow_future) is True


def test_shadow_loop_stop():
    sl.stop()
