import logging
import csv, io
import hashlib
from django.db import models
from urllib.request import urlopen
from django.http import HttpResponse
from api.models.image import Image

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

    def parse_row(self, row):
        if len(row) < 3:
            # TODO Throw exception
            return False

        title = row[0]
        description = row[1]
        url = row[2]
        # Get the image from the database in case it exists. If not create an object
        image = Image.objects.get_or_create(title=title, description=description, url=url, csv_id=self)[0]

        # If the image is not in the DB yet, validate and cache it
        if not image.image:
            image.validate_and_cache()
        return image

    def remove_unused_images(self, new_images):
        # Get the images stored referenced by the current CSV file
        stored_images = Image.objects.filter(csv_id=self)
        for stored_image in stored_images:
            if stored_image not in new_images:
                stored_image.delete()

    def load_csv(self):
        try:
            response = urlopen(self.url)
        except Exception:
            raise Exception("Imposible to load the image store: {0}".format(self.url))
        #TODO check if the CSV file has a header
        next(response)  # skip header row
        datareader = csv.reader(io.TextIOWrapper(response), delimiter=",")

        # Parse each row
        new_images = []
        total_urls = 0
        for row in datareader:
            total_urls += 1
            try:
                image = self.parse_row(row)
                image.save()
                new_images.append(image)
            except Exception as e:
                logger.error("Impossible to load image: {0}".format(e))
        self.generate_hash()
        self.remove_unused_images(new_images)
        logger.info("Images have been fetched: {0}/{1}.".format(len(new_images), total_urls))

