import logging
import os
from os.path import splitext, basename
from urllib.parse import urlparse
from django.db import models
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.core.files import File
from urllib.request import urlopen
from tempfile import NamedTemporaryFile


logger = logging.getLogger('imagestore')


class Image(models.Model):
    def generate_path(instance, filename):
        # Get the plain filename and extension from the URL and append it to the static path
        path = "images/"
        url = urlparse(filename)
        filename, file_ext = splitext(basename(url.path))
        full_path = os.path.join(path, filename + file_ext)
        return full_path

    title = models.CharField(max_length=120)
    description = models.TextField(null=True)
    url = models.URLField()
    image = models.ImageField(upload_to=generate_path)

    def validate_and_cache(self):
        if not self.title:
            raise ValidationError('The image has no title, which is required')
        if not self.url:
            raise ValidationError('The URL field is empty.')

        # Check that the URL is valid
        val = URLValidator()
        try:
            val(self.url)
        except ValidationError as e:
            raise ValidationError('The URL is not correctly formatted. Enter a valid URL')

        # Store the image in the server
        self.cache_image()

    def cache_image(self):
        img_temp = NamedTemporaryFile()
        response = urlopen(self.url)
        infor = response.info()
        header = dict(infor._headers)
        type = header['Content-Type']
        if 'image' not in type:
            raise ValidationError("The URL does not contains any image. (Content-Type: {0})".format(type))
        img_temp.write(response.read())
        img_temp.flush()

        self.image.save(self.url, File(img_temp))