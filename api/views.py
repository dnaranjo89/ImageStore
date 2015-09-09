import logging
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.serializers import ImageSerializer
from api.models.csv_file import CSVFile
from api.models.image import Image


logger = logging.getLogger('imagestore')


def populate(request):
    csv_file2 = CSVFile.objects.get_or_create(url="https://docs.google.com/spreadsheets/d/1cvSn15RCK8n-A-284FSquBxMd7GHsY9H2ysXMt6QUZc/export?format=csv&id=1cvSn15RCK8n-A-284FSquBxMd7GHsY9H2ysXMt6QUZc")[0]
    csv_file = CSVFile.objects.get_or_create(url="https://docs.google.com/spreadsheets/d/1QuGtCGCYp3RpVWlEHUD4HK42A6a5hYZSufE8RxMwfpM/export?format=csv&id=1QuGtCGCYp3RpVWlEHUD4HK42A6a5hYZSufE8RxMwfpM")[0]
    # Save to generate an ID
    csv_file.save()
    csv_file.load_csv()
    csv_file.save()

    csv_file2.save()
    csv_file2.load_csv()
    csv_file2.save()
    return HttpResponse("ok")


def check_updates():
    logger.info("check updates")
    stored_images = []
    csv_files = CSVFile.objects.all()
    for file in csv_files:
        if file.has_changed():
            new_images = file.load_csv()
            stored_images.append(new_images)


@api_view(['GET', ])
def get_image_list(request, format):
    if request.method == 'GET':
        # If the URL contains the parameter 'f', the sources will be checked for changes
        force_update = request.GET.get("f")
        if force_update is not None:
            check_updates()
        images = Image.objects.all()
        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data)
