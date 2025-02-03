from pydantic import BaseModel


class DataLoggerCreateSchema(BaseModel):
    name: str
    manufacturer: str
    sampling_rate: float
