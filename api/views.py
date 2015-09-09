import logging
from django.http import HttpResponse
from django.shortcuts import redirect
from rest_framework import generics
from api.serializers import ImageSerializer
from api.models.csv_file import CSVFile
from api.models.image import Image


logger = logging.getLogger('imagestore')


def optimize(request):
    image = Image(title='title1', description='Description1', url="http://img05.deviantart.net/9cab/i/2011/217/a/0/field_panorama_stock_5_by_f3rd4-d45kgfp.jpg")
    image.cache_image()
    cached_image = image.image
    return HttpResponse("ok")


def populate(request):
    csv_file = CSVFile(url="https://docs.google.com/spreadsheets/d/1QuGtCGCYp3RpVWlEHUD4HK42A6a5hYZSufE8RxMwfpM/export?format=csv&id=1QuGtCGCYp3RpVWlEHUD4HK42A6a5hYZSufE8RxMwfpM")
    csv_file.load_csv()
    csv_file.save()
    return HttpResponse("ok")


def check_updates():
    logger.info("check updates")
    csv_files = CSVFile.objects.all()
    for file in csv_files:
        if file.has_changed():
            file.load_csv()


def image_list_force_reload(request,format):
    check_updates()
    return redirect('image_list', format=format)


class ImageList(generics.ListCreateAPIView):
    # TODO Add decorator to check updates
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
