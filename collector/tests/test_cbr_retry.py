from decimal import Decimal

import httpx
import pytest

from app.clients.cbr import CbrClient
from app.clients.retry import is_retryable
from tests.test_cbr_client import BASE_URL, FIXTURE


async def test_retry_after_server_error() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(500)
        return httpx.Response(200, content=FIXTURE)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        rates = await CbrClient(http, BASE_URL).fetch_daily()

    assert [(r.code, r.rate) for r in rates] == [
        ('USD', Decimal('81.5012')),
        ('EUR', Decimal('94.1033')),
        ('JPY', Decimal('0.54321')),
    ]
    assert calls == 2


async def test_no_retry_on_404() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(404)
        return httpx.Response(200, content=FIXTURE)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        with pytest.raises(httpx.HTTPStatusError):
            await CbrClient(http, BASE_URL).fetch_daily()
    assert calls == 1


async def test_gives_up_after_3_timeouts() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ReadTimeout('slow', request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        with pytest.raises(httpx.ReadTimeout):
            await CbrClient(http, BASE_URL).fetch_daily()

    assert calls == 3


async def test_retry_after_429() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(429)
        return httpx.Response(200, content=FIXTURE)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        rates = await CbrClient(http, BASE_URL).fetch_daily()

    assert [(r.code, r.rate) for r in rates] == [
        ('USD', Decimal('81.5012')),
        ('EUR', Decimal('94.1033')),
        ('JPY', Decimal('0.54321')),
    ]
    assert calls == 2


async def test_predicate() -> None:
    request = httpx.Request('GET', 'https://cbr.test')
    error_502 = httpx.HTTPStatusError(
        'boom', request=request, response=httpx.Response(502, request=request)
    )
    error_404 = httpx.HTTPStatusError(
        'not found', request=request, response=httpx.Response(404, request=request)
    )
    transport_error = httpx.TransportError('oops', request=request)
    value_error = ValueError('oops')

    assert is_retryable(error_502)
    assert not is_retryable(error_404)
    assert is_retryable(transport_error)
    assert not is_retryable(value_error)
