# **************************************************************************
# *
# * Authors:    Pablo Conesa (pconesa@cnb.csic.es)
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
# *  e-mail address 'jmdelarosa@cnb.csic.es'
# *
# **************************************************************************
import os
from os.path import exists, join, basename, dirname

from django.http import HttpResponse
from django.shortcuts import render_to_response

import pyworkflow.utils as pwutils
from pyworkflow.em import ProtImportParticles
from pyworkflow.em.packages.xmipp3 import XmippProtReconstructSignificant, \
    XmippProtCropResizeParticles, XmippProtCropResizeVolumes, XmippProtValidateNonTilt
from pyworkflow.em.packages.xmipp3.protocol_validate_overfitting import XmippProtValidateOverfitting
from pyworkflow.tests.tests import DataSet
from pyworkflow.utils.utils import prettyDelta
from pyworkflow.web.app.views_base import base_grid
from pyworkflow.web.app.views_project import contentContext
from pyworkflow.web.app.views_protocol import contextForm
from pyworkflow.web.app.views_util import (getResourceCss, getResourceJs, getResourceIcon, getServiceManager,
                                           loadProtocolConf, CTX_PROJECT_PATH, CTX_PROJECT_NAME, PROJECT_NAME,
                                           getResource, getAbsoluteURL, MODE_SERVICE)
from pyworkflow.web.pages import settings as django_settings

MYPVAL_SERVICE = 'mypval'
MYPVAL_FORM_URL = 'p_form'


def particleValidation_projects(request):
    if CTX_PROJECT_NAME in request.session: request.session[CTX_PROJECT_NAME] = ""
    if CTX_PROJECT_PATH in request.session: request.session[CTX_PROJECT_PATH] = ""

    mypval_utils = getResource("js/mypval_utils.js")

    context = {'projects_css': getResourceCss('projects'),
               'project_utils_js': getResourceJs('project_utils'),
               'scipion_mail': getResourceIcon('scipion_mail'),
               'mypval_utils': mypval_utils,
               'hiddenTreeProt': True,
               }

    context = base_grid(request, context)
    return render_to_response('pval_projects.html', context)


def writeCustomMenu(customMenu):
    if not exists(customMenu):
        # Make the parent path if it doesn't exists
        pwutils.makePath(dirname(customMenu))

        f = open(customMenu, 'w+')
        f.write('''
[PROTOCOLS]

Reliability tools = [
    {"tag": "section", "text": "1. Import your data", "children": [
        {"tag": "protocol", "value": "ProtImportVolumes", "text": "import volumes", "icon": "bookmark.png"},
        {"tag": "protocol", "value": "ProtImportParticles", "text": "import particles", "icon": "bookmark.png"}]
    },
    {"tag": "section", "text": "2. Downsample", "children": [
        {"tag": "protocol", "value": "XmippProtCropResizeVolumes", "text": "xmipp3 - crop/resize volumes"},
        {"tag": "protocol", "value": "XmippProtCropResizeParticles", "text": "xmipp3 - crop/resize particles"}
        ]
    },
    {"tag": "section", "text": "3. Validate", "children": [
        {"tag": "protocol", "value": "XmippProtValidateOverfitting", "text": "xmipp3 - validate overfitting"},
        {"tag": "protocol", "value": "XmippProtValidateNonTilt", "text": "xmipp3 - alignment reliability"}
        ]
    }]
    ''')
        f.close()


def create_particleValidation_project(request):
    if request.is_ajax():
        from pyworkflow.em.protocol import ProtImportVolumes
        from pyworkflow.em.protocol import ProtImportParticles

        # Create a new project
        projectName = request.GET.get(PROJECT_NAME)

        # Filename to use as test data 
        testDataKey = request.GET.get('testData')

        manager = getServiceManager(MYPVAL_SERVICE)
        writeCustomMenu(manager.protocols)
        project = manager.createProject(projectName, runsView=1,
                                        hostsConf=manager.hosts,
                                        protocolsConf=manager.protocols,
                                        chdir=False
                                        )

        project.getSettings().setLifeTime(336)  # 14 days * 24 hours
        project.saveSettings()

        projectPath = manager.getProjectPath(projectName)

        # If we need to import test data...
        if testDataKey:

            # Get test data attributes
            attr = getAttrTestFile(testDataKey, projectPath)

            # 1. Import volumes
            source = attr['volume']
            dest = os.path.join(projectPath, 'Uploads', basename(source))
            pwutils.createLink(source, dest)

            label_import = "import volumes (" + testDataKey + ")"
            protImportVol = project.newProtocol(ProtImportVolumes, objLabel=label_import)

            protImportVol.filesPath.set(dest)
            protImportVol.samplingRate.set(attr['samplingRate'])
            project.launchProtocol(protImportVol, wait=True, chdir=False)

            # 2. Import particles
            binary = linkTestData(attr['particles'], projectPath)
            metaFile = linkTestData(attr['metaFile'], projectPath)

            label_import = "import particles (" + testDataKey + ")"
            protImportParticles = project.newProtocol(ProtImportParticles, objLabel=label_import)
            protImportParticles.filesPath.set(binary)

            # Set import particle attributes
            protImportParticles.importFrom.set(attr["importFrom"])

            # RELION Datasets
            if attr["importFrom"] == ProtImportParticles.IMPORT_FROM_RELION:
                protImportParticles.starFile.set(metaFile)
            else:
                protImportParticles.sqliteFile.set(metaFile)

            protImportParticles.voltage.set(attr["microscopeVoltage"])
            protImportParticles.sphericalAberration.set(attr["sphericalAberration"])
            protImportParticles.amplitudeContrast.set(attr["amplitudeContrast"])
            protImportParticles.magnification.set(attr["magnificationRate"])
            protImportParticles.samplingRate.set(attr["particlesSamplingRate"])

            project.launchProtocol(protImportParticles, wait=True, chdir=False)

            inputVolumeProtocol = protImportVol
            inputVolumeExtended = 'outputVolume'

            inputParticlesProtocol = protImportParticles
            inputParticlesExtended = 'outputParticles'

        else:

            # Empty import volumes protocol
            protImportVol = project.newProtocol(ProtImportVolumes, objLabel='import volume')
            project.saveProtocol(protImportVol)

            # Empty import particles protocol
            protImportParticles = project.newProtocol(ProtImportParticles, objLabel='import particles')
            project.saveProtocol(protImportParticles)


        inputVolumeProtocol = protImportVol
        inputVolumeExtended = 'outputVolume'

        inputParticlesProtocol = protImportParticles
        inputParticlesExtended = 'outputParticles'

        # 3a. Validate non tilt
        protNonTilt = project.newProtocol(XmippProtValidateNonTilt)
        protNonTilt.setObjLabel('alignment reliability (validate non tilt)')

        # link Input volumes
        protNonTilt.inputVolumes.set(inputVolumeProtocol)
        protNonTilt.inputVolumes.setExtended(inputVolumeExtended)

        # Input particles
        protNonTilt.inputParticles.set(inputParticlesProtocol)
        protNonTilt.inputParticles.setExtended(inputParticlesExtended)

        # Attributes
        if testDataKey:
            protNonTilt.symmetryGroup.set(attr['symmetry'])

        # Load additional configuration
        loadProtocolConf(protNonTilt)
        project.saveProtocol(protNonTilt)

        # 3b. Validation overfitting
        protValidation = project.newProtocol(XmippProtValidateOverfitting)
        protValidation.setObjLabel('BSOFT/xmipp3 - validate overfitting')

        # link Input volumes
        protValidation.input3DReference.set(inputVolumeProtocol)
        protValidation.input3DReference.setExtended(inputVolumeExtended)

        # Input particles
        protValidation.inputParticles.set(inputParticlesProtocol)
        protValidation.inputParticles.setExtended(inputParticlesExtended)

        # Attributes
        if testDataKey:
            protValidation.symmetryGroup.set(attr['symmetry'])
            protValidation.numberOfParticles.set(attr['numberOfParticles'])

        # Load additional configuration
        loadProtocolConf(protValidation)
        project.saveProtocol(protValidation)

    return HttpResponse(content_type='application/javascript')


def getAttrTestFile(key, projectPath):
    pval = DataSet.getDataSet('particle_validation')

    attr = None

    if key == "betagal":

        attr = {"path": pval.getPath(),
                "volume": pval.getFile("betagal_volume"),
                "samplingRate": 3.98,
                "particles": pval.getFile("betagal_particles"),
                "metaFile": pval.getFile("betagal_meta"),
                "microscopeVoltage": 300,
                "sphericalAberration": 2,
                "amplitudeContrast": 0.1,
                "magnificationRate": 50000,
                "particlesSamplingRate": 3.98,
                "symmetry": 'd2',
                "numberOfParticles": '10 20 50 100 200 500 1000 2000',
                "importFrom": ProtImportParticles.IMPORT_FROM_RELION
                }

        linkTestData(pval.getFile('betagal_optimizer'), projectPath)
        linkTestData(pval.getFile('betagal_half1'), projectPath)
        linkTestData(pval.getFile('betagal_half2'), projectPath)
        linkTestData(pval.getFile('betagal_sampling'), projectPath)

    elif key == "10004":

        attr = {"path": pval.getPath(),
                "volume": pval.getFile("10004_volume"),
                "samplingRate": 4.32,
                "particles": pval.getFile("10004_particles"),
                "metaFile": pval.getFile("10004_meta"),
                "microscopeVoltage": 80,
                "sphericalAberration": 2,
                "amplitudeContrast": 0.1,
                "magnificationRate": 75000,
                "particlesSamplingRate": 4.32,
                "symmetry": 'c3',
                "numberOfParticles": '10 20 50 100 200 500 1000 2000',
                "importFrom": ProtImportParticles.IMPORT_FROM_RELION
                }
        linkTestData(pval.getFile('10004_optimizer'), projectPath)
        linkTestData(pval.getFile('10004_half1'), projectPath)
        linkTestData(pval.getFile('10004_half2'), projectPath)
        linkTestData(pval.getFile('10004_sampling'), projectPath)

    elif key == "10008":

        attr = {"path": pval.getPath(),
                "volume": pval.getFile("10008_volume"),
                "samplingRate": 3.00,
                "particles": pval.getFile("10008_particles"),
                "metaFile": pval.getFile("10008_meta"),
                "microscopeVoltage": 200,
                "sphericalAberration": 2,
                "amplitudeContrast": 0.1,
                "magnificationRate": 50000,
                "particlesSamplingRate": 3.00,
                "symmetry": 'c3',
                "numberOfParticles": '10 20 50 100 200 500 1000 2000',
                "importFrom": ProtImportParticles.IMPORT_FROM_SCIPION
                }

    return attr


def linkTestData(fileToLink, projectPath):

    dest = os.path.join(projectPath, 'Uploads', basename(fileToLink))
    pwutils.createLink(fileToLink, dest)

    return dest


def particleValidation_form(request):
    from django.shortcuts import render_to_response
    context = contextForm(request)
    context.update({'path_mode': 'select',
                    'formUrl': MYPVAL_FORM_URL,
                    'showHost': False,
                    'showParallel': True})
    return render_to_response('form/form.html', context)


def particleValidation_content(request):
    projectName = request.GET.get('p', None)
    path_files = getAbsoluteURL('resources_mypval/img/')

    # Get info about when the project was created
    manager = getServiceManager(MYPVAL_SERVICE)
    project = manager.loadProject(projectName,
                                  protocolsConf=manager.protocols,
                                  hostsConf=manager.hosts,
                                  chdir=False)

    daysLeft = prettyDelta(project.getLeftTime())

    context = contentContext(request, project, serviceName=MYPVAL_SERVICE)

    # Resources for the help - guide, to be done.
    context.update({'formUrl': MYPVAL_FORM_URL,
                    'mode': MODE_SERVICE,
                    'daysLeft': daysLeft
                    })

    return render_to_response('pval_content.html', context)

