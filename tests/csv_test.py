from django.test import TestCase
from nose.tools import raises
from api.models import CSVFile

class CSVTest(TestCase):

    def setUp(self):
        pass

    def parametrized_constructor_test(self):
        """CSVFile: Basic construction"""
        CSVFile(url="https://docs.google.com/spreadsheets/d/1cvSn15RCK8n-A-284FSquBxMd7GHsY9H2ysXMt6QUZc/export?format=csv&id=1cvSn15RCK8n-A-284FSquBxMd7GHsY9H2ysXMt6QUZc")

    def load_content_ok_test(self):
        """CSVFile: Load content from CSV file"""
        csv_file = CSVFile(url="https://docs.google.com/spreadsheets/d/1cvSn15RCK8n-A-284FSquBxMd7GHsY9H2ysXMt6QUZc/export?format=csv&id=1cvSn15RCK8n-A-284FSquBxMd7GHsY9H2ysXMt6QUZc")
        csv_file.load_csv()
        self.assertIsNotNone(csv_file.hash)

    @raises(Exception)
    def load_content_ko_test(self):
        """CSVFile: Load content from incorrect URL"""
        csv_file = CSVFile(url="https://docs.google.com/spreadsheets/d/1cvSn15RCK8n-A-284FSquBxMHsY9H2ysXMt6QUZc/export?format=csv&id=1cvSn15RCK8n-A-284FSquBxMd79H2ysXMt")
        csv_file.load_csv()
