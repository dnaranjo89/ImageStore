import logging
import os
from os.path import splitext, basename
from urllib.parse import urlparse
from django.db import models
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.core.files import File
from urllib.request import urlopen, Request
from tempfile import NamedTemporaryFile

import tinify

tinify.key = "kqsvwgRVhpnG2DJNTIOJxVYVOmrBE08z"
logger = logging.getLogger('imagestore')


def optimize(data):
    try:
        optimized_data = tinify.from_buffer(data).to_buffer()
        return optimized_data
    except tinify.AccountError as e:
        # This exception may rise, since a Free account is being used (only 500 requests/month)
        logger.error("There is a problem with the TinyPNG Account: {0}".format(e))
        return data
    except tinify.ServerError as e:
        logger.error("There seem to be problems in the compression server: {0}".format(e))
        return data
    except Exception as e:
        logger.error("The image could not be compressed: {0}".format(e))
        return data


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
    csv_id = models.ForeignKey('CSVFile')

    def __eq__(self, other):
        if isinstance(other, Image):
            return self.url == other.url and self.title == other.title and self.description == other.description
        return NotImplemented

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
        # Header required for HTTPS connections
        request = Request(self.url, headers={'User-Agent': ''})
        response = urlopen(request)
        infor = response.info()
        header = dict(infor._headers)
        type = header['Content-Type']
        if 'image' not in type:
            raise ValidationError("The URL does not contains any image. (Content-Type: {0})".format(type))
        source_data = response.read()
        source_data = optimize(source_data)
        img_temp.write(source_data)
        img_temp.flush()

        self.image.save(self.url, File(img_temp))
