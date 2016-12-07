"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase
from django.test import Client
from models import Workflow
import json, urllib2
from tastypie.test import ResourceTestCase

example_content="""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head profile="http://selenium-ide.openqa.org/profiles/test-case">
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<link rel="selenium.base" href="http://0.0.0.0:8000/" />
<title>workflow</title>
</head>
<body>
<table cellpadding="1" cellspacing="1" border="1">
<thead>
<tr><td rowspan="1" colspan="3">workflow</td></tr>
</thead><tbody>
<tr>
	<td>open</td>
	<td>/workflowarchive/</td>
	<td></td>
</tr>
<tr>
	<td>type</td>
	<td>id=id_workflowName</td>
	<td>workflow_random</td>
</tr>
<tr>
	<td>type</td>
	<td>id=id_description</td>
	<td>Here goes a description of the tests</td>
</tr>
<tr>
	<td>type</td>
	<td>id=id_file</td>
	<td>/home/roberto/Scipion/scipion-web/pyworkflow/web/workflowarchive/HtmlTest/workflow.json</td>
</tr>
<tr>
	<td>clickAndWait</td>
	<td>css=button[type=&quot;submit&quot;]</td>
	<td></td>
</tr>
<tr>
	<td>assertText</td>
	<td>css=div.workFlowForm</td>
	<td>workflow uploaded </td>
</tr>

</tbody></table>
</body>
</html>"""

def deleteWorkflow( name):
    try:
        w = Workflow.objects.get(name=name)
        w.delete()
    except Workflow.DoesNotExist:
        pass

def createWorkflow( name, description, content):
    try:
        w = Workflow.objects.get(name=name)
    except Workflow.DoesNotExist:
        #w = Workflow(name=name, description=description, content=content)
        w = Workflow(name=name, description=description, content=content)
        w.save()
    return w

def findWorkflow( workflowId):
    try:
        w = Workflow.objects.get(id=workflowId)
    except Workflow.DoesNotExist:
        return None
    return w


class ModelsTest(TestCase):

    def setUp(self):
        #self.client   = Client()
        self.workflowContent = example_content
        self.workflowName = u"workflow_1"
        self.workflowName2 = u"workflow_2"
        self.workflowDescription = "description for workflow_1"
        self.workflowDescription2 = "description for workflow_2"


    def test_create_workflow(self):

        wIn = createWorkflow(self.workflowName,
                            self.workflowDescription,
                            self.workflowContent)

        wOut = findWorkflow(wIn.id)
        self.assertEqual(wIn, wOut)

        wIn2 = createWorkflow(self.workflowName2,
                            self.workflowDescription2,
                            self.workflowContent)

        wOut2 = findWorkflow(wIn2.id)
        self.assertEqual(wIn2, wOut2)

class WorkflowResourceTest(ResourceTestCase, TestCase):
    """Import this will not query the test data base!!!!"""

    def setUp(self):
        super(WorkflowResourceTest, self).setUp()
        self.client   = Client()
        self.workflowContent = example_content
        self.workflowName = u"workflow_11"
        self.workflowName2 = u"workflow_22"
        self.workflowDescription = "description for workflow_11"
        self.workflowDescription2 = "description for workflow_22"
        #webservice url
        #self.url = "http://127.0.0.1:8000"
        self.api = "/workflowarchive/api/workflow/"#?format=json

        #fill the database
        deleteWorkflow(self.workflowName)
        deleteWorkflow(self.workflowName2)

        wIn  = createWorkflow(self.workflowName,
                            self.workflowDescription,
                            self.workflowContent)

        wIn2 = createWorkflow(self.workflowName2,
                            self.workflowDescription2,
                            self.workflowContent)

    def test_query_single_object_Api(self):
        _url = self.api + "1/"
        resp = self.api_client.get(_url, format='json')
        _queryResultDic = self.deserialize(resp)
        self.assertEqual(_queryResultDic['name'],self.workflowName)

    def test_query_many_objects_Api(self):
        _url = self.api + "?name=%s"%self.workflowName2
        print _url
        resp = self.api_client.get(_url, format='json')
        _queryResultDic = self.deserialize(resp)
        q = _queryResultDic["objects"][0]
        self.assertEqual(q['name'],self.workflowName2)

        #retieve all stored workflows
        #_url = self.url + self.api + "?name=%s&format=json"%self.workflowName2
        #print json.load(urllib2.urlopen(_url))
