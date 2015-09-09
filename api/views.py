import logging
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.serializers import ImageSerializer
from api.models.csv_file import CSVFile
from api.models.image import Image


logger = logging.getLogger('imagestore')


def add_csv_file(url):
    """ Create a CSVFile object load its content and store everything in the DB """
    csv_file = CSVFile.objects.get_or_create(url=url)[0]
    # Save to generate an ID
    csv_file.save()
    # Load and store the images contained in the CSV file
    csv_file.load_csv()
    # Save to store the hash of the file
    csv_file.save()


def populate(request):
    """ Load the CSV files and the images that they reference and store them in the DB. """
    logger.debug("Load CSV files")
    csv_file_urls = [
        "https://docs.google.com/spreadsheets/d/1cvSn15RCK8n-A-284FSquBxMd7GHsY9H2ysXMt6QUZc/export?format=csv&id=1cvSn15RCK8n-A-284FSquBxMd7GHsY9H2ysXMt6QUZc",
        "https://docs.google.com/spreadsheets/d/1QuGtCGCYp3RpVWlEHUD4HK42A6a5hYZSufE8RxMwfpM/export?format=csv&id=1QuGtCGCYp3RpVWlEHUD4HK42A6a5hYZSufE8RxMwfpM",
    ]
    for url in csv_file_urls:
        add_csv_file(url)
    return HttpResponse("ok")


def check_updates():
    logger.info("check updates")
    stored_images = []
    csv_files = CSVFile.objects.all()
    for file in csv_files:
        if file.has_changed():
            logger.info("The following file has changed since last time. Fetching changes. (URL: {0})".format(file.url))
            new_images = file.load_csv()
            stored_images.append(new_images)


@api_view(['GET', ])
def get_image_list(request, format="api"):
    if request.method == 'GET':
        # If the URL contains the parameter 'f', the sources will be checked for changes
        force_update = request.GET.get("f")
        if force_update is not None:
            check_updates()
        images = Image.objects.all()
        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data)
