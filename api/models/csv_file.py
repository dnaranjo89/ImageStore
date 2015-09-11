import logging
import csv
import io
import hashlib
from urllib.error import URLError
from urllib.request import urlopen

from django.db import models
from django.contrib import admin
from django.core.exceptions import ValidationError

from api.models.image import Image

logger = logging.getLogger('imagestore')
logger_supplier = logging.getLogger('image_supplier')


def calculate_hash(url):
    """ Calculate the hash of a file
    :param url: URL where the file is located
    :return: The hash of the file
    """
    with urlopen(url) as file_to_check:
        # read contents of the file
        data = file_to_check.read()
        # pipe contents of the file through
        md5_returned = hashlib.md5(data).hexdigest()
        return md5_returned


class CSVFile(models.Model):
    """
    Manages a image file storage.
    Allows to parses a CSV file and download, compress and cache its content
    """
    url = models.URLField()
    hash = models.CharField(max_length=35, null=True, blank=True)

    def __str__(self):
        return self.url

    def generate_hash(self):
        """ Generate the hash of the CSV file which later on will be used to check whether the file has changed """
        self.hash = calculate_hash(self.url)

    def has_changed(self):
        """ Check if the CSV file has changed since the last time it was downloaded """
        return calculate_hash(self.url) != self.hash

    def remove_unused_images(self, new_images):
        """ Remove from the DB all the entries that belong to the current CSV file but are not in the 'new_images' lists
        :param new_images: The list of images that should remain in th DB
        """
        # Get the images stored referenced by the current CSV file
        stored_images = Image.objects.filter(csv_id=self)
        for stored_image in stored_images:
            if stored_image not in new_images:
                stored_image.delete()

    def parse_row(self, row):
        """
        Given a CSV row, parse it to generate an Image instance.
        If it pass the validation it will be stored in the server
        """
        if len(row) < 3:
            raise ValidationError("The row has less than 3 fields")

        title = row[0]
        description = row[1]
        url = row[2]
        # Get the image from the database in case it exists. If not create an object
        image = Image.objects.get_or_create(title=title, description=description, url=url, csv_id=self)[0]

        # If the image is not in the DB yet, validate and cache it
        if not image.image:
            image.validate_and_cache()
        return image

    def load_csv(self):
        """ Download and process the CSV file stored in 'self.url' """
        try:
            response = urlopen(self.url)
            # Skip header
            next(response)
            # Generate hash and store it in the DB
            self.generate_hash()
            self.save()
        except URLError:
            logger_supplier.info("Impossible to load the CSV file: {0}".format(self.url))
            logger.info("Impossible to load the CSV file: {0}".format(self.url))
        except StopIteration:
            logger_supplier.info("Couldn't load the CSV file. The file it's empty. (URL: {0}".format(self.url))
            logger.error("Couldn't load the CSV file. The file it's empty. (URL: {0}".format(self.url))
        else:
            datareader = csv.reader(io.TextIOWrapper(response), delimiter=",")
            # Parse each row
            new_images = []
            total_urls = 0
            for row in datareader:
                total_urls += 1
                try:
                    image = self.parse_row(row)
                except ValidationError as e:
                    logger_supplier.info("The image didn't pass the validation: {0}".format(e))
                    logger.error("The image didn't pass the validation: {0}".format(e))
                except Exception as e:
                    logger_supplier.info("Impossible to load the image: {0}".format(e))
                    logger.error("Impossible to load the image: {0}".format(e))
                else:
                    image.save()
                    new_images.append(image)

            self.remove_unused_images(new_images)
            logger.info("Images have been fetched: {0}/{1}.".format(len(new_images), total_urls))
            # Save to store the hash of the file


class CSVFileAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("hash", )
        form = super(CSVFileAdmin, self).get_form(request, obj, **kwargs)
        return form
