"""
Shadow-loop
~~~~~~~~~~~~~~~~~~~
Submit `awaitable` objects to a shadow event loop in a separate thread
and wait for their execution from synchronous code if needed.
:copyright: (c) 2018 isanich
:license: MIT, see LICENSE for more details.
"""
import logging
from .shadow_loop import ShadowLoop

logging.getLogger(__name__).addHandler(logging.NullHandler())