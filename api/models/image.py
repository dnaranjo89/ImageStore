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

    def generate_path(self, url):
        path = "images/"
        full_path = os.path.join(path, self.filename)
        return full_path

    title = models.CharField(max_length=120)
    description = models.TextField(null=True)
    url = models.URLField()
    image = models.ImageField(upload_to=generate_path)
    csv_id = models.ForeignKey('CSVFile')

    filename = ""

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
        type_file = dict(response.info()._headers)['Content-Type']
        if 'image' not in type_file:
            raise ValidationError("The URL does not contains any image. (Content-Type: {0})".format(type))
        # Store the filename with extension
        url_image = urlparse(self.url)
        filename, file_ext = splitext(basename(url_image.path))
        # If the file doesn't have a extension, find it out from the header
        if file_ext == '':
            file_ext = type_file.replace('image/', '')
        self.filename = filename + file_ext
        source_data = response.read()
        source_data = optimize(source_data)
        img_temp.write(source_data)
        img_temp.flush()

        self.image.save(self.url, File(img_temp))
