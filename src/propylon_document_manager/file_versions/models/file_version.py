from django.db import models
from django.conf import settings
from .file import File


class FileVersion(models.Model):
    file_obj = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
        related_name="versions"
    )
    version_number = models.IntegerField()
    file = models.FileField(upload_to="uploads/", null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="file_versions"
    )
    content_hash = models.CharField(max_length=64, editable=False, db_index=True) 