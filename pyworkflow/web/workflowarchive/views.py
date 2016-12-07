# Create your views here.
from django.http import HttpResponse
from workflowarchive.forms import FileUploadForm
from django.shortcuts import render
from app.views_util import loadProject, getResourceCss, getResourceIcon, getResourceJs
from app.views_base import base_grid
from models import Workflow
import json
import urllib2
def archive_workflow(request):
    context = {'projects_css': getResourceCss('projects'),
               'project_utils_js': getResourceJs('project_utils'),
               }
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            print "Valid form, save it"
            form.save()
            context['done']=True
        else:
            print "non valid"
            pass
        context['form']= form

    else:
        form = FileUploadForm()
        context['form']= form

    context =  base_grid(request, context)
    return render(request, 'wa_model_form_upload.html', context)

def list_workflow(request):

    workflows = Workflow.objects.all().order_by("-id")

    context = {'projects_css': getResourceCss('projects'),
               'project_utils_js': getResourceJs('project_utils'),
               'workflows': workflows,
               'host':request.META['HTTP_HOST']
               }

    context = base_grid(request, context)
    return render(request,'wa_workflows.html', context)

def download_workflow(request,workflow_id=1):
    _url = request.build_absolute_uri("/workflowarchive/api/workflow/%s/?format=json"%workflow_id)
    _workflow = json.load(urllib2.urlopen(_url))
    content =  _workflow['content']
    slugName =  _workflow['slug']
    #context = {'content': content}
    #return render(request,'wa_download.html', context)

    response = HttpResponse(content, mimetype='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' % (slugName)
    return response
