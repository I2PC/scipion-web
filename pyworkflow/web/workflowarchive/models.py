from django.db import models
from django.utils.text import slugify
from tastypie.utils.timezone import now

class Workflow(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=512, blank=True)
    content = models.CharField(max_length=16384)#For secury reasons this can not be unlimited
    slug = models.SlugField(null=True, blank=True)

    #name is going to work as PK and as part of URL
    #so we need to sanitize it (remove spaces, "/", etc
    def save(self, *args, **kwargs):
        # For automatic slug generation.
        if not self.slug:
            self.slug = slugify(self.name)[:50]

        return super(Workflow, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s (%d)"%(self.name, self.id)

