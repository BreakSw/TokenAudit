from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Any, Callable


def run_with_retry(
    fn: Callable[[], Any],
    *,
    timeout_s: float | None,
    retries: int,
    retry_delay_s: float,
) -> tuple[bool, Any, str]:
    last_err = ""
    for attempt in range(retries + 1):
        try:
            with ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(fn)
                if timeout_s is None or timeout_s <= 0:
                    return True, fut.result(), ""
                return True, fut.result(timeout=timeout_s), ""
        except TimeoutError:
            last_err = "timeout"
        except Exception as e:
            last_err = str(e) or e.__class__.__name__

        if attempt < retries:
            time.sleep(retry_delay_s)
    return False, None, last_err
