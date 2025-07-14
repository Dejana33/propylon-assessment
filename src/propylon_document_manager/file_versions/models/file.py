from django.db import models
from django.conf import settings


class File(models.Model):
    name = models.CharField(max_length=512)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="files"
    )

    def __str__(self):
        return self.name 