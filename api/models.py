import logging
import os, csv, io
import hashlib
from os.path import splitext, basename
from urllib.parse import urlparse
from django.db import models
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.core.files import File
from urllib.request import urlopen, Request
from tempfile import NamedTemporaryFile
from django.http import HttpResponse

logger = logging.getLogger('imagestore')


def calculate_hash(url):
    with urlopen(url) as file_to_check:
        # read contents of the file
        data = file_to_check.read()
        # pipe contents of the file through
        md5_returned = hashlib.md5(data).hexdigest()
        logger.error("MD5 ------------> " + str(md5_returned))
        return md5_returned


class CSVFile(models.Model):
    url = models.URLField()
    hash = models.CharField(max_length=120)

    def generate_hash(self):
        self.hash = calculate_hash(self.url)

    def has_changed(self):
        return calculate_hash(self.url) != self.hash

    def parse_row(request, row):
        if len(row) > 3:
            # TODO Throw exception
            return False

        title = row[0]
        description = row[1]
        url = row[2]
        image = Image(title=title, description=description, url=url)
        # Check if the image is already cached
        results = Image.objects.filter(url=url)
        if len(results) > 0:
            logger.debug("Image already stored in cache")
            image.image = results[0].image
        else:
            logger.debug("Trying to fetch image: " + url)
            image.validate_and_cache()
        return image

    def load_csv(self):
        try:
            response = urlopen(self.url)
        except Exception:
            raise Exception("Imposible to load the image store: {0}".format(self.url))
        #TODO check if the CSV file has a header
        next(response)  # skip header row
        datareader = csv.reader(io.TextIOWrapper(response), delimiter=",")

        # Parse each row
        total_urls = 0
        num_images_added = 0
        for row in datareader:
            total_urls += 1
            try:
                image = self.parse_row(row)
                image.save()
                num_images_added += 1
            except Exception as e:
                logger.error("Impossible to load image: {0}".format(e))
        self.generate_hash()
        logger.info("Images have been fetched: {0}/{1}.".format(num_images_added,total_urls))
        return HttpResponse("Images fetched successfully: {0}/{1}.".format(num_images_added,total_urls))


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
        # Header required for HTTPS connections
        request = Request(self.url, headers={'User-Agent': ''})
        response = urlopen(request)
        infor = response.info()
        header = dict(infor._headers)
        type = header['Content-Type']
        if 'image' not in type:
            raise ValidationError("The URL does not contains any image. (Content-Type: {0})".format(type))
        img_temp.write(response.read())
        img_temp.flush()

        self.image.save(self.url, File(img_temp))
