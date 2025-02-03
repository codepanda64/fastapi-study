from tortoise import fields
from tortoise.models import Model


class Network(Model):
    id = fields.IntField(primary_key=True)
    code = fields.CharField(max_length=5, unique=True)
    name = fields.CharField(max_length=20, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        table = "seismic_network"

    def __str__(self):
        return self.code


class Station(Model):
    id = fields.IntField(primary_key=True)
    network = fields.ForeignKeyField("models.Network", related_name="stations")
    code = fields.CharField(max_length=6)
    name = fields.CharField(max_length=20)
    position = fields.OneToOneField(
        "models.Position", related_name="station", null=True, default=None
    )
    address = fields.CharField(max_length=255, null=True, default=None)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # 设置联合唯一
    class Meta:
        unique_together = ("network", "code")
        table = "seismic_station"

    def __str__(self):
        return f"{self.network.code}/{self.code}"


class Position(Model):
    id = fields.IntField(primary_key=True)
    latitude = fields.FloatField()
    longitude = fields.FloatField()
    elevation = fields.FloatField(null=True)
    depth = fields.FloatField(null=True)
    is_virtual = fields.BooleanField()
    changed_at = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "seismic_position"
