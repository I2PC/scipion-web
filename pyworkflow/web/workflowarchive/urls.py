from django.conf.urls import patterns, url, include
import views
from api import WorkflowResource
workflow_resource = WorkflowResource()

urlpatterns = patterns('',
    url(r'^$', views.archive_workflow, name='archive_workflow'),
    url(r'^archive/$', views.archive_workflow, name='archive'),
    url(r'^list/$', views.list_workflow, name='list_workflow'),
    url(r'download/(?P<workflow_id>\d+)/',views.download_workflow,name='download_workflow'),
    url(r'^api/', include(workflow_resource.urls)),
)
