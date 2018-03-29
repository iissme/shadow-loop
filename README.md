# shadow-loop
[![Build Status](https://travis-ci.org/isanich/shadow-loop.svg?branch=master)](https://travis-ci.org/isanich/shadow-loop)
[![Coverage Status](https://coveralls.io/repos/github/isanich/shadow-loop/badge.svg?branch=master)](https://coveralls.io/github/isanich/shadow-loop?branch=master)

Python 3.6+

Submit _awaitable_ objects to a shadow event loop in a separate thread and wait for their execution from synchronous code if needed.

## Install
Clone from git and install via setup.py.
Or `pip install -U https://github.com/isanich/shadow-loop/archive/master.zip`.

## Documentation
Look at example below.
```py
import asyncio
from shadow_loop import ShadowLoop


async def coro():
    await asyncio.sleep(0.1)
    print('Shadow coroutine is done!')
    return True


async def coro_future(future):
    res = await coro()
    future.set_result(res)

# Debug argument is not required and leads to perfomance loss.
sl = ShadowLoop(debug=False)

# 'await_for' blocks until shadow_coro is done in shadow loop
#  and then returns its result (`True` in this case)
sl.await_for(coro())

# `create_task` creates asyncio.Task is shadow loop
task = sl.create_task(coro())
# You can wait for the task if needed
# and so `await_for` blocks until task is done and returns shadow_coro result (`True`)
sl.await_for(task)

# You can also create asyncio.Future that relates to shadow loop
# and use it as shown below for example
shadow_future = sl.create_future()
sl.create_task(coro_future(shadow_future))
sl.await_for(shadow_future)

# `stop` stops the loop and cancel all tasks in it if any exist
sl.stop()


# Shadow loop can be used from another asyncio loop but look at example below
async def await_fail():
    try:
        pending_shadow_task = sl.create_task(shadow_coro())
        # You can't `await` directly from another loop!
        # Use `sl.await_for(pending_task)` instead
        await pending_shadow_task
    except RuntimeError as e:
        print(e)  # if future is not finished before `await` you receive `RuntimeError`

local_loop = asyncio.get_event_loop()
local_loop.run_until_complete(async_await_fail())
```