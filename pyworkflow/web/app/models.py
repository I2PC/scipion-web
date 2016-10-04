from django.db import models

class Document(models.Model):

    class Meta:
        app_label = 'app'

    docfile = models.FileField(upload_to='uploads/')
