import csv
import io
import logging
from django.http import HttpResponse
from urllib.request import urlopen
from rest_framework import generics
from api.serializers import ImageSerializer
from api.models import Image


logger = logging.getLogger('imagestore')


class ImageList(generics.ListCreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


def parse_row(row):
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


def load_csv(request):
    url = "https://docs.google.com/spreadsheets/d/19CtR3Wuszozzpj2hj4lmcYpMPK9_c2Y9FQQsFigggeU/export?format=csv&id=19CtR3Wuszozzpj2hj4lmcYpMPK9_c2Y9FQQsFigggeU"
    response = urlopen(url)

    logger.info("start")
    #TODO check if the CSV file has a header
    next(response)  # skip header row
    datareader = csv.reader(io.TextIOWrapper(response), delimiter=",")

    # Parse each row
    total_urls = 0
    num_images_added = 0
    for row in datareader:
        total_urls += 1
        try:
            image = parse_row(row)
            image.save()
            num_images_added += 1
        except Exception as e:
            logger.error("Impossible to load image: {0}".format(e))
    logger.info("Images have been fetched: {0}/{1}.".format(num_images_added,total_urls))
    return HttpResponse("Images fetched successfully: {0}/{1}.".format(num_images_added,total_urls))