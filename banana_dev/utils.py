import time
from typing import Optional
from loguru import logger as _logger

def timer(t: Optional[float] = None, msg: Optional[str] = None, logger = _logger):
    if not t: return time.perf_counter()
    done_time = time.perf_counter() - t
    if msg: logger.info(f'Completed {msg} in {done_time:.2f} secs')
    return done_time