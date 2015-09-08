from django.db import models


class Image(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(null=True)
    url = models.URLField()
    filename = models.CharField(max_length=120)
    image = models.ImageField()
