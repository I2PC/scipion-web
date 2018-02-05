# **************************************************************************
# *
# * Authors:    Jose Gutierrez (jose.gutierrez@cnb.csic.es)
# *             Pablo Conesa (pconesa@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

from os.path import exists, join, basename

from django.http import HttpResponse
from django.shortcuts import render_to_response

import pyworkflow.utils as pwutils
from pyworkflow.em.packages.bsoft import BsoftProtBlocres
from pyworkflow.em.packages.xmipp3 import XmippProtMonoRes, ProtImportMask, \
    XmippProtCreateMask3D
from pyworkflow.em.packages.resmap import ProtResMap
from pyworkflow.tests.tests import DataSet
from pyworkflow.utils.utils import prettyDelta
from pyworkflow.utils import makeFilePath
from pyworkflow.web.app.views_base import base_grid
from pyworkflow.web.app.views_project import contentContext
from pyworkflow.web.app.views_protocol import contextForm
from pyworkflow.web.app.views_util import (getResourceCss, getResourceJs, getResourceIcon, getServiceManager,
                                           loadProtocolConf, CTX_PROJECT_PATH, CTX_PROJECT_NAME, PROJECT_NAME,
                                           getResource, getAbsoluteURL, MODE_SERVICE)
from pyworkflow.web.pages import settings as django_settings

MYRESMAP_SERVICE = 'myresmap'


def resmap_projects(request):
    if CTX_PROJECT_NAME in request.session: request.session[CTX_PROJECT_NAME] = ""
    if CTX_PROJECT_PATH in request.session: request.session[CTX_PROJECT_PATH] = ""

    myresmap_utils = getResource("js/myresmap_utils.js")

    context = {'projects_css': getResourceCss('projects'),
               'project_utils_js': getResourceJs('project_utils'),
               'scipion_mail': getResourceIcon('scipion_mail'),
               'myresmap_utils': myresmap_utils,
               'hiddenTreeProt': True,
               }

    context = getToolContext(context)

    context = base_grid(request, context)
    return render_to_response('resmap_projects.html', context)


def getToolContext(context):
    imagesURL = getToolImagesURL()
    resolutionContext = {'toolImages': imagesURL}
    resolutionContext.update(context)
    return resolutionContext


def writeCustomMenu(customMenu):
    if not exists(customMenu):
        makeFilePath(customMenu)
        f = open(customMenu, 'w+')
        f.write('''
[PROTOCOLS]

Local_Resolution = [
    {"tag": "section", "text": "2. Import your data", "children": [
        {"tag": "protocol", "value": "ProtImportVolumes", "text": "import volumes", "icon": "bookmark.png"},
        {"tag": "protocol", "value": "ProtImportMask", "text": "import mask", "icon": "bookmark.png"}]},
    {"tag": "section", "text": "3. Local resolution tools", "children": [
        {"tag": "protocol", "value": "XmippProtCreateMask3D", "text": "xmipp3 - create 3D mask"},
        {"tag": "protocol", "value": "ProtResMap", "text": "resmap - local resolution"},
        {"tag": "protocol", "value": "XmippProtMonoRes", "text": "monores - local resolution"},
        {"tag": "protocol", "value": "BsoftProtBlocres", "text": "bsoft - local resolution"}
        ]}]
        ''')
        f.close()


def create_resmap_project(request):
    if request.is_ajax():
        import os
        from pyworkflow.em.protocol import ProtImportVolumes
        from pyworkflow.em.packages.resmap.protocol_resmap import ProtResMap

        # Create a new project
        projectName = request.GET.get(PROJECT_NAME)

        # Filename to use as test data 
        testDataKey = request.GET.get('testData')

        manager = getServiceManager(MYRESMAP_SERVICE)
        writeCustomMenu(manager.protocols)
        project = manager.createProject(projectName, runsView=1,
                                        hostsConf=manager.hosts,
                                        protocolsConf=manager.protocols,
                                        chdir=False
                                        )

        project.getSettings().setLifeTime(336)  # 14 days * 24 hours
        project.saveSettings()

        projectPath = manager.getProjectPath(projectName)

        # 1. Import maps
        if testDataKey:
            attr = getAttrTestFile(testDataKey)
            source = attr['file']
            dest = os.path.join(projectPath, 'Uploads', basename(source))
            pwutils.createLink(source, dest)

            label_import = "import volumes (" + testDataKey + ")"
            protImport = project.newProtocol(ProtImportVolumes, objLabel=label_import)

            protImport.filesPath.set(dest)
            protImport.samplingRate.set(attr['samplingRate'])

            project.launchProtocol(protImport, wait=True)
        else:
            protImport = project.newProtocol(ProtImportVolumes, objLabel='import volumes')
            project.saveProtocol(protImport)

            # BlocRes
            protBlocRes = project.newProtocol(BsoftProtBlocres)
            # protBlocRes.inputVolume.set(protImport)
            # protBlocRes.inputVolume.setExtended('outputVolume.1')
            # protBlocRes.inputVolume2.set(protImport)
            # protBlocRes.inputVolume2.setExtended('outputVolume.2')
            setProtocolParams(protBlocRes, None)
            project.saveProtocol(protBlocRes)


        # 2. Mask
        protMask = project.newProtocol(XmippProtCreateMask3D)
        protMask.inputVolume.set(protImport)
        protMask.inputVolume.setExtended('outputVolume')
        setProtocolParams(protMask, testDataKey)
        project.saveProtocol(protMask)

        # 3. ResMap
        protResMap = project.newProtocol(ProtResMap)
        protResMap.setObjLabel('resmap - local resolution')
        protResMap.inputVolume.set(protImport)
        protResMap.inputVolume.setExtended('outputVolume')
        protResMap.applyMask.set(True)
        protResMap.maskVolume.set(protMask)
        protResMap.maskVolume.setExtended('outputMask')
        setProtocolParams(protResMap, testDataKey)
        project.saveProtocol(protResMap)

        # 4. MonoRes
        protMonoRes = project.newProtocol(XmippProtMonoRes)
        protMonoRes.setObjLabel('monores - local resolution')
        protMonoRes.inputVolumes.set(protImport)
        protMonoRes.inputVolumes.setExtended('outputVolume')
        protMonoRes.Mask.set(protMask)
        protMonoRes.Mask.setExtended('outputMask')
        setProtocolParams(protMonoRes, testDataKey)
        project.saveProtocol(protMonoRes)

    return HttpResponse(content_type='application/javascript')


def getAttrTestFile(key):
    resmap = DataSet.getDataSet('resmap')

    if key == "fcv":
        attr = {"file": resmap.getFile("fcv"),
                "samplingRate": 2.33,
                }

    if key == "t20s_proteasome":
        attr = {"file": resmap.getFile("t20s_full"),
                "samplingRate": 0.98,
                }

    if key == "betagal":
        attr = {"file": resmap.getFile("betagal_map"),
                "samplingRate": 0.637,
                }

    return attr


def resmap_form(request):
    from django.shortcuts import render_to_response
    context = contextForm(request)
    context.update({'path_mode': 'select',
                    'formUrl': 'my_form',
                    'showHost': False,
                    'showParallel': True})
    return render_to_response('form/form.html', context)


def resmap_content(request):
    projectName = request.GET.get('p', None)
    path_files = getToolImagesURL()

    # Get info about when the project was created
    manager = getServiceManager(MYRESMAP_SERVICE)
    project = manager.loadProject(projectName,
                                  protocolsConf=manager.protocols,
                                  hostsConf=manager.hosts,
                                  chdir=False)

    daysLeft = prettyDelta(project.getLeftTime())

    context = contentContext(request, project, serviceName=MYRESMAP_SERVICE)
    context.update({'importVolumes': path_files + 'importVolumes.png',
                    'useResMap': path_files + 'useResMap.png',
                    'protResMap': path_files + 'protResMap.png',
                    'analyzeResults': path_files + 'analyzeResults.png',
                    'formUrl': 'r_form',
                    'mode': MODE_SERVICE,
                    'daysLeft': daysLeft
                    })

    return render_to_response('resmap_content.html', context)

def setProtocolParams(protocol, key):
    # Here we set protocol parameters for each test data
    if key:
        cls = type(protocol)

        if issubclass(cls, XmippProtCreateMask3D):
            if key == "fcv":
                attrs = {"threshold": 0.8
                         }
            if key == "betagal":
                attrs = {"threshold": 0.047
                         }
            if key == "t20s_proteasome":
                attrs = {"threshold": 0.006,
                "doSmall": True,
                "doBig": True,
                "doMorphological": True,
                "morphologicalOperation": 0
                         }

        elif issubclass(cls, ProtResMap):
            if key == "fcv":
                attrs = {"prewhitenAng": 12.52,
                         "prewhitenRamp": 0.97,
                         "stepRes": 0.25
                         }
            if key == "betagal":
                attrs = {"prewhitenAng": 4.94,
                         "prewhitenRamp": 1.0,
                         "stepRes": 0.25,
                         "minRes": 1.0,
                         "maxRes": 5.0
                         }
            if key == "t20s_proteasome":
                attrs = {"prewhitenAng": 7.92,
                         "prewhitenRamp": 1.0,
                         "stepRes": 0.25,
                         "minRes": 1.0,
                         "maxRes": 6.0
                         }

        elif issubclass(cls, XmippProtMonoRes):
            if key == "fcv":
                attrs = {"symmetry": "I",
                         "stepSize": 0.25
                         }
            if key == "betagal":
                attrs = {"symmetry": "d2",
                         "maxRes": 5.0
                         }

            if key == "t20s_proteasome":
                attrs = {"symmetry": "c7",
                         "stepSize": 0.25,
                         "maxRes": 6.0
                         }

        for key, value in attrs.iteritems():
            getattr(protocol, key).set(value)

    loadProtocolConf(protocol)

def getToolImagesURL():

    return getAbsoluteURL('resources_myresmap/img/')
