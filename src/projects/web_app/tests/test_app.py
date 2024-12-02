import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_read_main(
        _async_client: AsyncClient,
):
    response = await _async_client.get("/")
    assert response.status_code == 200
