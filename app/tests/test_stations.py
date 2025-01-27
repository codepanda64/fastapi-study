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
async def create_station(client: AsyncClient, create_network) -> AsyncGenerator:
    network_data = create_network
    network_id = network_data["id"]
    response = await client.post(
        "/api/stations",
        json={"network_id": network_id, "code": "STA1", "name": "Station 1"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    station_data = response.json()
    yield station_data


@pytest.fixture
async def create_station_with_current_position(
    client: AsyncClient, create_station
) -> AsyncGenerator:
    station_data = create_station
    station_id = station_data["id"]
    response = await client.post(
        f"/api/stations/{station_id}/positions",
        json={
            "latitude": 25.0,
            "longitude": 100.0,
            "elevation": 1700.0,
            "depth": 10.0,
            "change_time": "2022-01-01T00:00:00",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    station_data = response.json()
    yield station_data


@pytest.fixture
async def create_multiple_stations(
    client: AsyncClient, create_network
) -> AsyncGenerator:
    network_data = create_network
    network_id = network_data["id"]
    response = await client.post(
        "/api/stations",
        json={"network_id": network_id, "code": "STA1", "name": "Station 1"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    response = await client.post(
        "/api/stations",
        json={"network_id": network_id, "code": "STA2", "name": "Station 2"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    yield


@pytest.mark.anyio
async def test_create_station(client: AsyncClient, create_network) -> None:
    network_data = create_network
    network_id = network_data["id"]
    response = await client.post(
        "/api/stations",
        json={"network_id": network_id, "code": "STA1", "name": "Station 1"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["code"] == "STA1"
    assert data["name"] == "Station 1"


@pytest.mark.anyio
async def test_create_station_about_unique(client: AsyncClient, create_station) -> None:
    response = await client.post(
        "/api/stations",
        json={"network_id": 1, "code": "STA1", "name": "Station 1"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == 'Station with code "STA1" already exists'


@pytest.mark.anyio
async def test_create_station_about_code_length(client: AsyncClient) -> None:
    response = await client.post(
        "/api/stations",
        json={"network_id": 1, "code": "ST", "name": "Station 1"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == (
        "String should have at least 3 characters"
    )
    response = await client.post(
        "/api/stations",
        json={"network_id": 1, "code": "STA123456", "name": "Station 1"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == (
        "String should have at most 6 characters"
    )


@pytest.mark.anyio
async def test_create_station_without_network(client: AsyncClient) -> None:
    response = await client.post(
        "/api/stations",
        json={"network_id": None, "code": "STA1", "name": "Station 1"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_create_station_with_wrong_network_id(client: AsyncClient) -> None:
    response = await client.post(
        "/api/stations",
        json={"network_id": 1, "code": "STA1", "name": "Station 1"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_create_station_with_position(
    client: AsyncClient, create_network
) -> None:
    network_data = create_network
    network_id = network_data["id"]
    response = await client.post(
        "/api/stations",
        json={
            "network_id": network_id,
            "code": "STA1",
            "name": "Station 1",
            "position": {
                "latitude": 25.0,
                "longitude": 100.0,
                "elevation": 1700.0,
                "depth": 10.0,
                "change_time": "2022-01-01T00:00:00",
            },
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["code"] == "STA1"
    assert data["name"] == "Station 1"
    assert data["current_position"]["latitude"] == 25.0
    assert data["current_position"]["longitude"] == 100.0
    assert data["current_position"]["elevation"] == 1700.0
    assert data["current_position"]["depth"] == 10.0


@pytest.mark.anyio
async def test_station_add_position(client: AsyncClient, create_station) -> None:
    station_data = create_station
    station_id = station_data["id"]
    response = await client.post(
        f"/api/stations/{station_id}/positions",
        json={
            "latitude": 25.0,
            "longitude": 100.0,
            "elevation": 1700.0,
            "depth": 10.0,
            "change_time": "2022-01-01T00:00:00",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.anyio
async def test_station_add_same_position(
    client: AsyncClient, create_station_with_current_position
) -> None:
    station_data = create_station_with_current_position
    station_id = station_data["id"]
    response = await client.post(
        f"/api/stations/{station_id}/positions",
        json={
            "latitude": 25.0,
            "longitude": 100.0,
            "elevation": 1700.0,
            "depth": 10.0,
            "change_time": "2022-01-01T00:00:00",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_get_station(client: AsyncClient, create_station) -> None:
    station_data = create_station
    station_id = station_data["id"]
    response = await client.get(f"/api/stations/{station_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["code"] == "STA1"
    assert data["name"] == "Station 1"


@pytest.mark.anyio
async def test_get_station_with_current_position(
    client: AsyncClient, create_station
) -> None:
    station_data = create_station
    station_id = station_data["id"]
    response = await client.get(f"/api/stations/{station_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["code"] == "STA1"
    assert data["name"] == "Station 1"


@pytest.mark.anyio
async def test_get_stations(client: AsyncClient, create_multiple_stations) -> None:
    response = await client.get("/api/stations")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) == 2
    assert data[0]["code"] == "STA1"
    assert data[1]["code"] == "STA2"


@pytest.mark.anyio
async def test_get_stations_by_network(
    client: AsyncClient, create_network, create_multiple_stations
) -> None:
    network_data = create_network
    network_id = network_data["id"]
    response = await client.get(f"/api/stations?network_id={network_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) == 2
    assert data[0]["code"] == "STA1"
    assert data[1]["code"] == "STA2"


@pytest.mark.anyio
async def test_update_station(client: AsyncClient, create_station) -> None:
    station_data = create_station
    station_id = station_data["id"]
    network_id = station_data["network_id"]
    response = await client.put(
        f"/api/stations/{station_id}",
        json={"network_id": network_id, "code": "STA3", "name": "Station 3"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["network_id"] == network_id
    assert data["code"] == "STA3"
    assert data["name"] == "Station 3"


@pytest.mark.anyio
async def test_delete_station(client: AsyncClient, create_station) -> None:
    station_data = create_station
    station_id = station_data["id"]
    response = await client.delete(f"/api/stations/{station_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
