from django.conf.urls import patterns, url
from workflowarchive import views
from workflowarchive.api import WorkflowResource

urlpatterns = patterns('',
    url(r'^$', views.archive_workflow, name='archive_workflow'),
    url(r'^archive/$', views.archive_workflow, name='archive'),
    url(r'^list/$', views.list_workflow, name='list_workflow'),
)
