from django.test import TestCase
from nose.tools import assert_raises, raises
from api.models.image import Image
import django
from django.core.exceptions import ValidationError


class ImageTest(TestCase):

    def setUp(self):
        pass

    def default_constructor_test(self):
        """Image: Basic construction"""
        Image()

    def parametrized_constructor_test(self):
        """Image: Basic construction"""
        image = Image(title='title1', description='Description1', url="http://www.test.com")

    def cache_image_ok_test(self):
        """Image: Cache image"""
        image = Image(title='title1', description='Description1', url="http://comps.canstockphoto.com/can-stock-photo_csp9177473.jpg")
        image.cache_image()
        cached_image = image.image
        self.assertIsNotNone(cached_image)

    @raises(ValidationError)
    def cache_image_ko_test(self):
        """Image: URL does not contain an image"""
        image = Image(title='title1', description='Description1', url="http://www.google.com")
        image.cache_image()

    def validate_image_ok_test(self):
        """Image: Validate image and cache"""
        image = Image(title='title1', description='Description1', url="http://comps.canstockphoto.com/can-stock-photo_csp9177473.jpg")
        image.validate_and_cache()
        cached_image = image.image
        self.assertIsNotNone(cached_image)

    @raises(ValidationError)
    def validate_image_url_ko_test(self):
        """Image: Validate image (empty URL)"""
        image = Image(title='title1', description='Description1')
        image.validate_and_cache()
        cached_image = image.image
        self.assertIsNotNone(cached_image)

    @raises(ValidationError)
    def validate_image_title_ko_test(self):
        """Image: Validate image (empty title)"""
        image = Image(description='Description1', url="http://comps.canstockphoto.com/can-stock-photo_csp9177473.jpg")
        image.validate_and_cache()
        cached_image = image.image
        self.assertIsNotNone(cached_image)

    @raises(Exception)
    def validate_image_404_ko_test(self):
        """Image: Validate image (ERROR 404)"""
        image = Image(title='title1', description='Description1', url="http://echaloasuerte.com/asdsad")
        image.validate_and_cache()
        cached_image = image.image
        self.assertIsNotNone(cached_image)

