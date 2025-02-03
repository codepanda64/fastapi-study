from tortoise.models import Model
from tortoise import fields


class UploadedFile(Model):
    id = fields.IntField(pk=True)
    file_name = fields.CharField(max_length=255)
    file_path = fields.CharField(max_length=255)
    uploaded_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "common_uploaded_files"
