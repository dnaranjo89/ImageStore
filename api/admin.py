from django.contrib import admin
from api.models.csv_file import CSVFile, CSVFileAdmin

admin.site.register(CSVFile, CSVFileAdmin)
