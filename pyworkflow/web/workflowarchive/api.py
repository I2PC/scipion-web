from tastypie.resources import ModelResource
from tastypie.constants import ALL
from tastypie.utils import trailing_slash
from django.conf.urls import url
import json
from collections import Counter

from models import Workflow


class WorkflowResource(ModelResource):
    """allow search in workflow table"""
    """http://0.0.0.0:8000/workflowarchive/api/workflow/?format=json
    You should get back a list of Workflow-like objects.
    http://0.0.0.0:8000/workflowarchive/api/workflow/?format=json&id=1
    http://127.0.0.1:8000/workflowarchive/api/workflow/?format=json
    http://127.0.0.1:8000/workflowarchive/api/workflow/1/?format=json
    http://127.0.0.1:8000/workflowarchive/api/workflow/schema/?format=json
    http://127.0.0.1:8000/workflowarchive/api/workflow/set/1;3/?format=json
    http://127.0.0.1:8000/workflowarchive/api/workflow/?uploaded_at__gte=2017-01-01&format=json
    """

    class Meta:
        queryset = Workflow.objects.all()
        resource_name = 'workflow'
        filtering = {'id': ALL,
                     'name': ALL,
                     'slug': ALL,
                     'uploaded_at': ['exact', 'lt', 'lte', 'gte', 'gt'],
                     }
        excludes = ['id','name','uploaded_at','description','resource_uri']
        allowed_methods = ['get']
