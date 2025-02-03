from tortoise.models import Model
from tortoise import fields


class StationHistory(Model):
    id = fields.IntField(pk=True)
    station = fields.ForeignKeyField("models.Station")
    is_current = fields.BooleanField(default=False)
    changed_at = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        abstract = True


class StationPositionHistory(StationHistory):
    station = fields.ForeignKeyField(
        "models.Station", related_name="position_histories"
    )
    latitude = fields.FloatField()
    longitude = fields.FloatField()
    elevation = fields.FloatField(null=True)
    depth = fields.FloatField(null=True)
    is_virtual = fields.BooleanField(default=False)

    class Meta:
        table = "histories_station_position"


class StationObservationSystemHistory(StationHistory):
    station = fields.ForeignKeyField("models.Station", related_name="os_histories")
    observation_system = fields.ForeignKeyField(
        "models.ObservationSystem", related_name="station_histories"
    )

    class Meta:
        table = "histories_station_observation_system"
