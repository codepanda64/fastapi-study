from tortoise.models import Model
from tortoise import fields

from app.models.seismic import Station


class DataLogger(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255)
    sampling_rate = fields.FloatField()
    # 其他数据采集器相关字段

    class Meta:
        table = "instruments_data_loggers"


class Seismometer(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255)
    sensitivity = fields.FloatField()
    # 其他地震仪相关字段

    class Meta:
        table = "instruments_seismometers"


class IntegratedSeismometer(DataLogger, Seismometer):
    # 一体机继承自 DataLogger 和 Seismometer
    # 可以添加一体机特有的字段
    firmware_version = fields.CharField(max_length=50)

    class Meta:
        table = "instruments_integrated_seismometers"


# 设备实体基类
class DeviceInstance(Model):
    id = fields.IntField(primary_key=True)
    serial_number = fields.CharField(max_length=255, unique=True)  # 序列号
    production_date = fields.DateField()  # 出厂日期
    status = fields.CharField(max_length=50)  # 使用状态（如 "active", "inactive"）

    class Meta:
        abstract = True  # 抽象基类，不会创建数据库表


# 数据采集器实体
class DataLoggerInstance(DeviceInstance):
    data_logger = fields.ForeignKeyField(
        "models.DataLogger", related_name="instances"
    )  # 关联到数据采集器型号

    class Meta:
        unique_together = ("serial_number", "data_logger")
        table = "instruments_data_logger_instances"


# 地震仪实体
class SeismometerInstance(DeviceInstance):
    seismometer = fields.ForeignKeyField(
        "models.Seismometer", related_name="instances"
    )  # 关联到地震仪型号

    class Meta:
        unique_together = ("serial_number", "seismometer")
        table = "instruments_seismometer_instances"


# 一体机实体
class IntegratedSeismometerInstance(DeviceInstance):
    integrated_seismometer = fields.ForeignKeyField(
        "models.IntegratedSeismometer", related_name="instances"
    )  # 关联到一体机型号

    class Meta:
        unique_together = ("serial_number", "integrated_seismometer")
        table = "instruments_integrated_seismometer_instances"


from tortoise.models import Model
from tortoise import fields
from tortoise.exceptions import ValidationError


class ObservationSystem(Model):
    id = fields.IntField(primary_key=True)
    station = fields.ForeignKeyField(
        "models.Station", related_name="observation_systems"
    )

    # 引用数据采集器实体和地震仪实体
    data_logger_instance = fields.ForeignKeyField(
        "models.DataLoggerInstance",
        related_name="observation_systems_as_data_logger",
        null=True,
    )
    seismometer_instance = fields.ForeignKeyField(
        "models.SeismometerInstance",
        related_name="observation_systems_as_seismometer",
        null=True,
    )

    # 引用一体机实体
    integrated_seismometer_instance = fields.ForeignKeyField(
        "models.IntegratedSeismometerInstance",
        related_name="observation_systems_as_integrated",
        null=True,
    )

    async def save(self, *args, **kwargs):
        # 验证观测系统的组成
        if not (
            (self.data_logger_instance and self.seismometer_instance)
            or self.integrated_seismometer_instance
        ):
            raise ValidationError(
                "观测系统必须由数据采集器实体和地震仪实体组成，或者由一体机实体组成。"
            )
        await super().save(*args, **kwargs)

    class Meta:
        table = "instruments_observation_systems"
