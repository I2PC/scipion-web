from tastypie.resources import ModelResource
from tastypie.constants import ALL
from django.conf.urls import url
from tastypie.utils import trailing_slash
import json
from collections import Counter

from models import Workflow


class WorkflowResource(ModelResource):
    """allow search in workflow table"""
    class Meta:
        queryset = Workflow.objects.all()
        resource_name = 'workflow'
        filtering = {'id': ALL,
                     'name': ALL,
                     'uploaded_at': ['exact', 'lt', 'lte', 'gte', 'gt'],
                     }

