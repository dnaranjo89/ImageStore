import csv
import io
import logging
import hashlib
from django.http import HttpResponse
from urllib.request import urlopen
from django.shortcuts import redirect
from rest_framework import generics
from api.serializers import ImageSerializer
from api.models import Image, CSVFile


logger = logging.getLogger('imagestore')


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


def image_list_force_reload(request):
    logger.info("show list")
    check_updates()
    return redirect('image_list')


class ImageList(generics.ListCreateAPIView):
    # TODO Add decorator to check updates
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
