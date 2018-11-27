from django.db import models


class Base(models.Model):
    """A base class with common fields for all """
    created = models.DateTimeField(auto_now_add=True, help_text="This is the time of creation of this record")
    modified = models.DateTimeField(auto_now=True, help_text="This field is updated any time this record is updated")
