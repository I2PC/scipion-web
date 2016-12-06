# Create your views here.
from workflowarchive.forms import FileUploadForm
from django.shortcuts import render
from app.views_util import loadProject, getResourceCss, getResourceIcon, getResourceJs
from app.views_base import base_grid
from models import Workflow

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
    workflows = Workflow.objects.all()

    context = {'projects_css': getResourceCss('projects'),
               'project_utils_js': getResourceJs('project_utils'),
               'workflows': workflows
               }

    context = base_grid(request, context)

    return render(request,'wa_workflows.html', context)
