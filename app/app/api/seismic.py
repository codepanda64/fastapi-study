from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.models.seismic import Network, Position, Station

from tortoise.query_utils import Prefetch
from tortoise.transactions import atomic
from tortoise.exceptions import IntegrityError, ValidationError

from app.schemas.seismic import (
    NetworkIn,
    NetworkOut,
    PositionIn,
    PositionOut,
    StationIn,
    StationOut,
    StationSimpleOut,
)

router = APIRouter()


@router.get(
    "/networks",
    response_model=List[NetworkOut],
    summary="Get all networks",
    description="Get all networks",
)
async def get_networks(
    skip: int = 0,
    limit: int = 10,
    order_by: List[str] = Query(["code"], description="Order by fields"),
):
    networks = await Network.all().order_by(*order_by).offset(skip).limit(limit)
    return networks


@router.get("/networks/{network_id}", response_model=NetworkOut)
async def get_network(network_id: int):
    network = await Network.get_or_none(id=network_id)
    if not network:
        raise HTTPException(status_code=404, detail="Network not found")
    return network


@router.post(
    "/networks", response_model=NetworkOut, status_code=status.HTTP_201_CREATED
)
async def create_network(network: NetworkIn):
    try:
        import pydantic

        print(pydantic.__version__)
        network_obj = await Network.create(**network.model_dump())
        return network_obj
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Network with code "{network.code}" already exists',
        )


@router.put("/networks/{network_id}", response_model=NetworkOut)
async def update_network(network_id: int, network: NetworkIn):
    network_obj = await Network.get_or_none(id=network_id)
    if not network_obj:
        raise HTTPException(status_code=404, detail="Network not found")

    update_data = network.model_dump()
    has_changed = False

    for key, value in update_data.items():
        if getattr(network_obj, key) != value:
            setattr(network_obj, key, value)
            has_changed = True

    if has_changed:
        await network_obj.save()

    return network_obj


@router.delete("/networks/{network_id}", status_code=204)
async def delete_network(network_id: int):
    network_obj = await Network.get_or_none(id=network_id)
    if not network_obj:
        raise HTTPException(status_code=404, detail="Network not found")
    await network_obj.delete()
    return JSONResponse(status_code=204, content=None)


async def get_stations_query(
    network_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 10,
    order_by: List[str] = Query(
        ["network__code", "code"], description="Order by fields"
    ),
):
    # 确保 stations 是一个 QuerySet
    if network_id:
        stations = Station.filter(network_id=network_id)
    else:
        stations = Station.all()
    # 统一处理预加载和排序
    stations = (
        await stations.select_related("network")
        .prefetch_related(
            Prefetch("positions", queryset=Position.filter(is_current=True))
        )
        .order_by(*order_by)
        .offset(skip)
        .limit(limit)
    )

    return stations


@router.get("/stations", response_model=List[StationOut])
@router.get("/networks/{network_id}/stations", response_model=List[StationOut])
async def get_stations(stations: List[Station] = Depends(get_stations_query)):
    for station in stations:
        station.current_position = next(iter(station.positions), None)

    return stations


async def get_station_or_404(station_id: int):
    station = (
        await Station.filter(id=station_id)
        .select_related("network")
        .prefetch_related(
            Prefetch("positions", queryset=Position.filter(is_current=True))
        )
        .first()
    )
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return station


@router.get("/stations/{station_id}", response_model=StationOut)
async def get_station(station: Station = Depends(get_station_or_404)):
    station.current_position = next(iter(station.positions), None)
    return station


@router.post(
    "/stations", response_model=StationSimpleOut, status_code=status.HTTP_201_CREATED
)
@atomic()  # 使用事务确保数据一致性
async def create_station(station: StationIn):
    try:
        # 提取 station 和 position 数据
        station_data = station.model_dump(exclude={"position"})  # 排除 position 字段

        # 创建 Station 对象
        station_obj = await Station.create(**station_data)

        if station.position:
            position_data = station.position.model_dump()
            # 创建 Position 对象并关联到 Station
            position_obj = await Position.create(**position_data, station=station_obj)
            # 将 position 赋值给 station 的 current_position 字段
            station_obj.current_position = position_obj

        # 返回完整的 StationSimpleOut 响应
        return station_obj
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Station with code "{station.code}" already exists',
        )


@router.put("/stations/{station_id}", response_model=StationOut)
@atomic()
async def update_station(
    new_station: StationIn, old_station: Station = Depends(get_station_or_404)
):
    update_data = new_station.model_dump(exclude={"position"})
    for key, value in update_data.items():
        setattr(old_station, key, value)

    await old_station.save()

    if new_station.position:
        position_data = new_station.position.model_dump()
        await Position.filter(station=old_station, is_current=True).bulk_update(
            is_current=False
        )

        current_postion_obj = await Position.create(
            **position_data, station=old_station, is_current=True
        )
        old_station.current_position = current_postion_obj
    return old_station


@router.delete("/stations/{station_id}")
async def delete_station(station_id: int):
    station_obj = await Station.get_or_none(id=station_id)
    if not station_obj:
        raise HTTPException(status_code=404, detail="Station not found")
    await station_obj.delete()
    return JSONResponse(
        status_code=204,
        content={"message": "Station deleted"},
    )


@router.post(
    "/stations/{station_id}/positions",
    response_model=StationOut,
    status_code=status.HTTP_201_CREATED,
)
async def update_station_position(station_id: int, position: PositionIn):
    station_obj = await Station.get_or_none(id=station_id).select_related("network")

    if not station_obj:
        raise HTTPException(status_code=404, detail="Station not found")

    position_obj = Position(**position.model_dump())

    last_position_obj = await Position.get_or_none(
        station_id=station_id, is_current=True
    )
    if last_position_obj:
        if (
            abs(last_position_obj.latitude - position_obj.latitude) < 0.0001
            and abs(last_position_obj.longitude - position_obj.longitude) < 0.0001
        ):
            print("No change")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Position has not changed",
            )

        await Position.filter(station_id=station_id, is_current=True).update(
            is_current=False
        )

    position_obj.station = station_obj
    await position_obj.save()

    station_obj.current_position = position_obj
    return station_obj


@router.get("/stations/{station_id}/positions", response_model=List[PositionOut])
async def get_station_positions(station_id: int):
    station = await Station.get_or_none(id=station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    positions = await station.positions.order_by("-change_time").all()
    return positions


@router.patch("/positions/{position_id}/set_current", response_model=PositionOut)
async def set_position_is_current(position_id: int):
    position_obj = await Position.get_or_none(id=position_id)
    if not position_obj:
        raise HTTPException(status_code=404, detail="Position not found")
    station = await position_obj.station
    await Position.filter(station=station, is_current=True).update(is_current=False)
    position_obj.is_current = True
    await position_obj.save()
    return position_obj


@router.delete("/positions/{position_id}")
async def delete_position(position_id: int):
    position_obj = await Position.get_or_none(id=position_id)
    if not position_obj:
        raise HTTPException(status_code=404, detail="Position not found")
    await position_obj.delete()
    return JSONResponse(
        status_code=204,
        content={"message": "Position deleted"},
    )
