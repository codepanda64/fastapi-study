# tests/test_networks.py
from typing import AsyncGenerator
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.fixture
async def create_network(client: AsyncClient) -> AsyncGenerator:
    response = await client.post(
        "/api/networks", json={"code": "NET1", "name": "Network 1"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    network_data = response.json()
    yield network_data


@pytest.fixture
async def create_multiple_networks(client: AsyncClient) -> AsyncGenerator:
    await client.post("/api/networks", json={"code": "NET1", "name": "Network 1"})
    await client.post("/api/networks", json={"code": "NET2", "name": "Network 2"})
    yield


@pytest.mark.anyio
async def test_create_network(client: AsyncClient) -> None:
    response = await client.post(
        "/api/networks", json={"code": "NET1", "name": "Network 1"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["code"] == "NET1"
    assert data["name"] == "Network 1"


@pytest.mark.anyio
async def test_create_network_about_unique(client: AsyncClient, create_network) -> None:
    response = await client.post(
        "/api/networks", json={"code": "NET1", "name": "Network 1"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == 'Network with code "NET1" already exists'


@pytest.mark.anyio
async def test_create_network_about_code_length(client: AsyncClient) -> None:
    response = await client.post(
        "/api/networks", json={"code": "N", "name": "Network 1"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    print(response.json())
    assert response.json()["detail"][0]["msg"] == (
        "String should have at least 2 characters"
    )
    response = await client.post(
        "/api/networks", json={"code": "NET123", "name": "Network 2"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    print(response.json())
    assert response.json()["detail"][0]["msg"] == (
        "String should have at most 5 characters"
    )


@pytest.mark.anyio
async def test_get_networks(client: AsyncClient, create_multiple_networks) -> None:
    response = await client.get("/api/networks")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) == 2
    assert data[0]["code"] == "NET1"
    assert data[1]["code"] == "NET2"

    response = await client.get("/api/networks?skip=1&limit=1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["code"] == "NET2"

    response = await client.get("/api/networks?order_by=code")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data[0]["code"] == "NET1"
    assert data[1]["code"] == "NET2"

    response = await client.get("/api/networks?order_by=-code")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data[0]["code"] == "NET2"
    assert data[1]["code"] == "NET1"


@pytest.mark.anyio
async def test_get_network(client: AsyncClient, create_network) -> None:
    network_data = create_network
    network_id = network_data["id"]
    response = await client.get(f"/api/networks/{network_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["code"] == "NET1"
    assert data["name"] == "Network 1"


@pytest.mark.anyio
async def test_update_network(client: AsyncClient, create_network) -> None:
    network_data = create_network
    network_id = network_data["id"]
    response = await client.put(
        f"/api/networks/{network_id}", json={"code": "NET3", "name": "Network 3"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["code"] == "NET3"
    assert data["name"] == "Network 3"


@pytest.mark.anyio
async def test_delete_network(client: AsyncClient, create_network) -> None:
    network_data = create_network
    network_id = network_data["id"]
    response = await client.get(f"/api/networks/{network_id}")
    assert response.status_code == 200

    response = await client.delete(f"/api/networks/{network_id}")
    assert response.status_code == 204

    response = await client.get(f"/api/networks/{network_id}")
    assert response.status_code == 404
