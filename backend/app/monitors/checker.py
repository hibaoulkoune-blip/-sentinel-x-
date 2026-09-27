import asyncio
import time
from dataclasses import dataclass

import aiohttp


@dataclass
class CheckResult:
    status: str
    status_code: int | None
    response_time_ms: float | None
    error: str | None


async def check_url(
    url: str,
    timeout_seconds: int = 10,
) -> CheckResult:
    start_time = time.perf_counter()

    timeout = aiohttp.ClientTimeout(total=timeout_seconds)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                elapsed = (time.perf_counter() - start_time) * 1000
                response_time_ms = round(elapsed, 2)

                if 200 <= response.status < 400:
                    return CheckResult(
                        status="UP",
                        status_code=response.status,
                        response_time_ms=response_time_ms,
                        error=None,
                    )

                return CheckResult(
                    status="DOWN",
                    status_code=response.status,
                    response_time_ms=response_time_ms,
                    error=f"HTTP error: {response.status}",
                )

    except asyncio.TimeoutError:
        elapsed = (time.perf_counter() - start_time) * 1000

        return CheckResult(
            status="DOWN",
            status_code=None,
            response_time_ms=round(elapsed, 2),
            error="Request timeout",
        )

    except aiohttp.ClientError as exc:
        elapsed = (time.perf_counter() - start_time) * 1000

        return CheckResult(
            status="DOWN",
            status_code=None,
            response_time_ms=round(elapsed, 2),
            error=str(exc),
        )

    except Exception as exc:
        elapsed = (time.perf_counter() - start_time) * 1000

        return CheckResult(
            status="DOWN",
            status_code=None,
            response_time_ms=round(elapsed, 2),
            error=str(exc),
        )