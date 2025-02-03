from enum import Enum
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.schemas.histories import StationPositionHistoryOut
from app.models.histories import StationPositionHistory
from app.models.seismic import Network, Position, Station

from tortoise.query_utils import Prefetch
from tortoise.transactions import atomic
from tortoise.exceptions import IntegrityError, ValidationError

from app.schemas.seismic import (
    NetworkIn,
    NetworkOut,
    PositionIn,
    StationIn,
    StationOut,
    StationSimpleIn,
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
        await stations.select_related("network", "position")
        .order_by(*order_by)
        .offset(skip)
        .limit(limit)
    )

    return stations


@router.get("/stations", response_model=List[StationOut])
@router.get("/networks/{network_id}/stations", response_model=List[StationOut])
async def get_stations(stations: List[Station] = Depends(get_stations_query)):
    return stations


async def get_station_or_404(station_id: int):
    station = (
        await Station.filter(id=station_id)
        .select_related("network", "position")
        .first()
    )
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return station


@router.get("/stations/{station_id}", response_model=StationOut)
async def get_station(station: Station = Depends(get_station_or_404)):
    return station


class MethodType(str, Enum):
    MAP = "map"
    REAL = "real"

    def __str__(self):
        return self.value


@router.post(
    "/stations/", response_model=StationSimpleOut, status_code=status.HTTP_201_CREATED
)
@atomic()  # 使用事务确保数据一致性
async def create_station(
    station_schema: StationIn,
    method_type: Optional[MethodType] = None,
):
    # 参数预验证
    if method_type and not station_schema.position:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Position is required with method type",
        )
    try:
        # 创建 Station 对象
        station_data = station_schema.model_dump(exclude={"position"})
        station_obj = await Station.create(**station_data, position=None)
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Station with code "{station_schema.code}" already exists',
        )

    # 不需要处理位置信息的情况
    if not method_type:
        return station_obj

    # 处理位置信息创建
    position_data = station_schema.position.model_dump()
    position_data["is_virtual"] = method_type == MethodType.MAP

    # 创建 Position 对象并关联到 Station
    position_obj = await Position.create(**position_data)
    station_obj.position = position_obj
    await station_obj.save()

    # 创建位置变更历史记录
    await _update_position_history(station_obj, position_obj, is_new=True)
    return station_obj


def _is_same_position(position_obj: Position, position_dict: dict) -> bool:
    """
    判断两个位置是否相同
    """
    return (
        abs(position_obj.latitude - position_dict["latitude"]) < 0.0001
        and abs(position_obj.longitude - position_dict["longitude"]) < 0.0001
    )


async def _update_position(existing_position: Position, position_dict: dict):
    if _is_same_position(existing_position, position_dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Position unchanged",
        )
    existing_position.update_from_dict(position_dict)
    await existing_position.save()


async def _update_position_history(station: Station, position: Position, is_new=False):
    """
    更新 Position 历史记录
    """
    if not is_new:
        # 禁用当前的历史记录
        await StationPositionHistory.filter(station=station, is_current=True).update(
            is_current=False
        )
    # 创建新的历史记录
    await StationPositionHistory.create(
        station=station,
        latitude=position.latitude,
        longitude=position.longitude,
        elevation=position.elevation,
        depth=position.depth,
        changed_at=position.changed_at,
        is_current=True,
    )


@router.put("/stations/{station_id}", response_model=StationOut)
@atomic()
async def update_station(
    station_schema: StationSimpleIn, station_obj: Station = Depends(get_station_or_404)
):
    """
    更新 Station 对象
    """
    update_data = station_schema.model_dump()
    station_obj.update_from_dict(update_data)
    await station_obj.save()
    return station_obj


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


@router.put(
    "/stations/{station_id}/position",
    response_model=StationOut,
    status_code=status.HTTP_200_OK,
    description="Update station position",
)
@atomic()
async def station_set_position(
    position_schema: PositionIn,
    station_obj: Station = Depends(get_station_or_404),
    method_type: MethodType = MethodType.REAL,
):
    position_data = position_schema.model_dump()
    position_data["is_virtual"] = method_type == MethodType.MAP
    if station_obj.position:

        if method_type == MethodType.MAP:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Only the first position can be set to the 'map' method",
            )
        is_new = False
        # 如果台站存在位置，更新位置
        await _update_position(station_obj.position, position_data)
    else:
        is_new = True
        # 如果台站不存在位置，创建位置
        station_obj.position = await Position.create(**position_data)
        await station_obj.save()

    # 更新位置历史记录
    await _update_position_history(station_obj, station_obj.position, is_new)

    return station_obj


@router.get(
    "/stations/{station_id}/position/histories",
    response_model=List[StationPositionHistoryOut],
)
async def get_station_position_histories(station_id: int):
    station = await Station.get_or_none(id=station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    position_histories = await station.position_histories.all()
    return position_histories


@router.delete("/position/histories/{position_history_id}", status_code=204)
async def delete_position(position_id: int):
    position_history_obj = await StationPositionHistory.get_or_none(id=position_id)
    if not position_history_obj:
        raise HTTPException(status_code=404, detail="Position history not found")
    await position_history_obj.delete()
    return JSONResponse(
        status_code=204,
        content={"message": "Position history deleted"},
    )
