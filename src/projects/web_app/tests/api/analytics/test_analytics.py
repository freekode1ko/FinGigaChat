import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_menu(
        _async_client: AsyncClient,
):
    response = await _async_client.get("/api/v1/analytics/menu")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_section(_async_client: AsyncClient, ):
    response = await _async_client.get("/api/v1/analytics/section/1")
    assert response.status_code == 200
