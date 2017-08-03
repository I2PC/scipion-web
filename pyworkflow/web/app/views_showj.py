# **************************************************************************
# *
# * Authors:    Jose Gutierrez (jose.gutierrez@cnb.csic.es)
# *             Adrian Quintana (aquintana@cnb.csic.es)
# *             
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

import os
from django.http import HttpResponse
from pyworkflow.web.pages import settings as django_settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from pyworkflow.web.app.views_util import readDimensions, readImageVolume, getResourceJs, getResourceCss, \
    getProjectPathFromRequest, GET, getResource
from forms import ShowjForm
from pyworkflow.em import *
from layout_configuration import ColumnPropertiesEncoder
from views_base import base_showj
import pyworkflow.em.showj as sj
import subprocess


def loadDataSet(request, inputParams, firstTime):
    """ Load the DataSet from the session or from file. Also load some table.
    Params:
        request: web request variable, where dataset can be in session.
        filename: the path from where to load the dataset.
        firstTime: if True, for to load from file
    """
    filename = inputParams[sj.PATH]

    if firstTime or not sj.DATASET in request.session:
        dataset = loadDatasetXmipp(filename)
    else:
        dataset = request.session[filename][sj.DATASET]

    return dataset


def loadTable(request, dataset, inputParams):
    if inputParams[sj.TABLE_NAME] is not None:
        updateTable(inputParams, dataset)

    dataset.projectPath = getProjectPathFromRequest(request)
    table = dataset.getTable(inputParams[sj.TABLE_NAME])

    # Update inputParams to make sure have a valid table name (if using first table)
    inputParams[sj.TABLE_NAME] = dataset.currentTable()

    return table


def updateTable(inputParams, dataset):
    """ Save changes in the SQLITE before to load a new table
     to keep the changes in the elements."""

    listChanges = inputParams[sj.CHANGES]
    tableName = inputParams[sj.TABLE_NAME]

    if len(listChanges) > 0:
        items = listChanges.split(",")
        for x in items:
            item = x.split("-")
            id = item[0]
            state = item[1]
        #            print "CHANGES TO SAVE:", id," - "+ state
    else:
        #        print "NO CHANGES"
        pass


def hasTableChanged(request, inputParams):
    return request.session.get(inputParams[sj.PATH], {}).get(sj.TABLE_NAME, None) != inputParams.get(sj.TABLE_NAME,
                                                                                                     None)


def loadColumnsConfig(request, dataset, table, inputParams, extraParams, firstTime):
    """ Load table layout configuration. How to display columns and attributes (visible, render, editable) """
    tableChanged = hasTableChanged(request, inputParams)

    # Clear table name and selected volume after a table change
    if not firstTime and tableChanged:
        inputParams[sj.VOL_SELECTED] = None

    if firstTime or tableChanged:
        # getting defaultColumnsLayoutProperties
        columnsProperties, _ = getExtraParameters(extraParams, table)
        request.session[sj.COLS_CONFIG_DEFAULT] = columnsProperties

        # getting tableLayoutConfiguration
        allowRender = inputParams[sj.ALLOW_RENDER]
        columnsConfig = sj.ColumnsConfig(table, allowRender, columnsProperties)
        request.session[sj.COLS_CONFIG] = columnsConfig

    else:
        # getting tableLayoutConfiguration from Session
        columnsConfig = request.session[sj.COLS_CONFIG]

    inputParams[sj.COLS_CONFIG] = columnsConfig
    setLabelToRender(request, table, inputParams, extraParams, firstTime)


def addProjectPrefix(request, fn):
    """ Split path in block and filename and add the project path to filename. """
    projectPath = getProjectPathFromRequest(request)

    if projectPath is None:
        raise Exception('Showj Web visualizer: No project loaded')

    if '@' in fn:
        parts = fn.split('@')
        return join('%s@%s' % (parts[0], join(projectPath, parts[1])))
    else:
        return join(projectPath, fn)


def getRenderableColumnsFromParams(extraParams, table):
    columnsProperties, mapCol = getExtraParameters(extraParams, table)
    labelsToRender = []

    for x in columnsProperties:
        if 'renderable' in columnsProperties[x]:
            if columnsProperties[x]['renderable'] == "True":
                labelsToRender.append(mapCol[x])

    if len(labelsToRender) == 0:
        labelsToRender = None
    return labelsToRender


def setLabelToRender(request, table, inputParams, extraParams, firstTime):
    """ If no label is set to render, set the first one if exists """
    labelAux = inputParams.get(sj.LABEL_SELECTED, False)
    hasChanged = hasTableChanged(request, inputParams)

    if (not labelAux or hasChanged):
        labelsToRender = getRenderableColumnsFromParams(extraParams, table)
        labelsToRender, _ = inputParams[sj.COLS_CONFIG].getRenderableColumns(extra=labelsToRender)

        if labelsToRender:
            inputParams[sj.LABEL_SELECTED] = labelsToRender[0]
        else:
            # If there is no image to display and it is initial load, switch to table mode 
            if firstTime:
                inputParams[sj.MODE] = sj.MODE_TABLE

            inputParams[sj.LABEL_SELECTED] = ''

    table.setLabelToRender(inputParams[sj.LABEL_SELECTED])


def setRenderingOptions(request, dataset, table, inputParams):
    """ Read the first renderizable item and setup some variables.
    For example, if we are in volume mode or not.
    """
    # Setting the _typeOfColumnToRender
    label = inputParams[sj.LABEL_SELECTED]
    _imageVolNameOld = ""

    if not label:
        volPath = None
        _imageDimensions = ''
        _stats = None
        inputParams[sj.IMG_ZOOM] = 0
        inputParams[sj.MODE] = sj.MODE_TABLE
        dataset.setNumberSlices(0)
    else:
        # Setting the _imageVolName
        _imageVolName = inputParams[sj.VOL_SELECTED]
        if _imageVolName == None:
            _imageVolName = table.getValueFromIndex(0, label)

        _typeOfColumnToRender = inputParams[sj.COLS_CONFIG].getColumnProperty(label, 'columnType')
        isVol = _typeOfColumnToRender == sj.COL_RENDER_VOLUME
        oldMode = inputParams[sj.OLDMODE]

        if isVol:
            if oldMode == None or oldMode not in ['table', 'gallery']:
                _imageVolName = inputParams[sj.VOL_SELECTED] or table.getValueFromIndex(0, label)
            else:
                if oldMode == inputParams[sj.MODE]:
                    # No mode change
                    if oldMode == 'table':
                        pass
                    elif oldMode == 'gallery':
                        _imageVolName = inputParams[sj.VOL_SELECTED]
                        index = table.getIndexFromValue(_imageVolName, label) + 1
                        inputParams[sj.SELECTEDITEMS] = index

                elif oldMode != inputParams[sj.MODE]:
                    # Mode changed
                    if oldMode == 'gallery':
                        # New Functionality used to mark elements rendered in gallery mode for volumes
                        _imageVolName = inputParams[sj.VOL_SELECTED]
                    elif oldMode == 'table':
                        # New Functionality used to render elements selected in table mode for volumes
                        lastItemSelected = inputParams[sj.SELECTEDITEMS].split(',').pop()
                        if len(lastItemSelected) > 0:
                            index = int(lastItemSelected) - 1
                        else:
                            # To avoid exceptions without selected item between transitions
                            index = 0

                        _imageVolName = table.getValueFromIndex(index, label)
                        inputParams[sj.VOL_SELECTED] = _imageVolName

        if _imageVolName is None:
            # Patch to visualize individual volume
            pathAux = inputParams[sj.PATH].split("/Runs/")[1]
            _imageVolName = "Runs/" + pathAux

        # Setting the _imageDimensions
        _imageDimensions = readDimensions(request, _imageVolName, _typeOfColumnToRender)

        if _imageDimensions is None:
            dataset.setNumberSlices(None)
        else:
            dataset.setNumberSlices(_imageDimensions[2])

        if _typeOfColumnToRender == sj.COL_RENDER_IMAGE or isVol:
            is3D = inputParams[sj.MODE] ==sj.MODE_VOL_NGL
            # Setting the _convert
            _convert = isVol and (inputParams[sj.MODE] in [sj.MODE_GALLERY, sj.MODE_TABLE] or is3D)
            # Setting the _reslice
            _reslice = isVol and inputParams[sj.MODE] in [sj.MODE_GALLERY, sj.MODE_TABLE]
            # Setting the _getStats
            _getStats = isVol and is3D
            # Setting the _dataType
            _dataType = xmipp.DT_FLOAT if isVol and inputParams[sj.MODE] == sj.MODE_VOL_NGL else xmipp.DT_UCHAR
            # Setting the _imageVolName and _stats

            # CONVERSION TO .mrc DONE HERE!
            _imageVolNameOld = _imageVolName
            _imageVolNameNew, _stats = readImageVolume(request, _imageVolName, _convert, _dataType, _reslice,
                                                       int(inputParams[sj.VOL_VIEW]), _getStats)

            if isVol:
                inputParams[sj.COLS_CONFIG].configColumn(label, renderFunc="get_slice")
                dataset.setVolumeName(_imageVolName)
            else:
                if inputParams[sj.MODE] != sj.MODE_TABLE:
                    inputParams[sj.MODE] = sj.MODE_GALLERY

        volPath = os.path.join(getProjectPathFromRequest(request), _imageVolName)

    return volPath, _stats, _imageDimensions, _imageVolNameOld


# Initialize default values
DEFAULT_PARAMS = {
    sj.PATH: None,
    sj.ALLOW_RENDER: True,  # Image can be displayed, depending on column layout
    sj.MODE: sj.MODE_GALLERY,  # Mode Options: gallery, table, column, volume_astex, volume_chimera
    sj.TABLE_NAME: None,  # Table name to display. If None the first one will be displayed
    sj.LABEL_SELECTED: None,  # Column to be displayed in gallery mode. If None the first one will be displayed
    sj.GOTO: 1,
# Element selected (metadata record) by default. It can be a row in table mode or an image in gallery mode
    sj.MANUAL_ADJUST: 'Off',
# In gallery mode 'On' means columns can be adjust manually by the user. When 'Off' columns are adjusted automatically to screen width.
    sj.COLS: None,  # In gallery mode (and colRowMode set to 'On') cols define number of columns to be displayed
    sj.ROWS: None,  # In gallery mode (and colRowMode set to 'On') rows define number of columns to be displayed

    sj.ORDER: None,
    sj.SORT_BY: None,
    sj.IMG_ZOOM: '128px',  # Zoom set by default
    sj.IMG_MIRRORY: False,  # When 'True' image are mirrored in Y Axis
    sj.IMG_APPLY_TRANSFORM: False,  # When 'True' if there is transform matrix, it will be applied
    sj.IMG_ONLY_SHIFTS: False,  # When 'True' if there is transform matrix, only shifts will be applied
    sj.IMG_WRAP: False,  # When 'True' if there is transform matrix, only shifts will be applied
    sj.IMG_MAX_WIDTH: 512,  # Maximum image width (in pixels)
    sj.IMG_MIN_WIDTH: 64,  # Minimum image width (in pixels)
    sj.IMG_MAX_HEIGHT: 512,  # Maximum image height (in pixels)
    sj.IMG_MIN_HEIGHT: 64,  # Minimum image height (in pixels)

    sj.VOL_SELECTED: None,
# If 3D, Volume to be displayed in gallery, volume_astex and volume_chimera mode. If None the first one will be displayed
    sj.VOL_VIEW: xmipp.VIEW_Z_NEG,  # If 3D, axis to slice volume
    sj.VOL_TYPE: 'map',
# If map, it will be displayed normally, else if pdb only astexViewer and chimera display will be available

    sj.SELECTEDITEMS: 0,  # List with the id for the selected items in the before mode.
    sj.ENABLEDITEMS: 0,  # List with the id for the enabled items in the before mode.
    sj.CHANGES: 0,  # List with the changes done
    sj.OLDMODE: None,
}


def showj(request):
    """ This method will visualize data objects in table or gallery mode.
    Columns can be customized to be rendered, visible or more...
    This method can be called in two modes:
    GET: the first time the parameters will be parsed from GET request.
    POST: next call to the method will be done through POST, some parameters will
         be store also in SESSION
    """
    firstTime = request.method == GET

    # =TIME CONTROL==============================================================
    #    from datetime import datetime
    #    start = datetime.now()
    #    print "INIT SHOWJ: ", datetime.now()-start
    # ===========================================================================

    ### WEB INPUT PARAMETERS ###
    _imageDimensions = ''
    _imageVolName = ''
    _stats = None
    dataset = None
    table = None
    volPath = None

    inputParams = DEFAULT_PARAMS.copy()
    extraParams = {}

    if firstTime:
        for key, value in request.GET.iteritems():
            if key in inputParams:
                inputParams[key] = value
            else:
                extraParams[key] = value
        inputParams[sj.PATH] = addProjectPrefix(request, inputParams[sj.PATH])

        cleanSession(request, inputParams[sj.PATH])
    else:
        for key, value in request.POST.iteritems():
            if key in inputParams:
                inputParams[key] = value
                # extraParams will be read from SESSION

    # Image zoom 
    request.session[sj.IMG_ZOOM_DEFAULT] = inputParams[sj.IMG_ZOOM]

    # =DEBUG=====================================================================
    #    from pprint import pprint
    #    print "INPUT PARAMS:"
    #    pprint(inputParams)
    #    print "EXTRA PARAMS:"
    #    pprint(extraParams)
    # ===========================================================================

    if inputParams[sj.VOL_TYPE] != 'pdb':
        # Load the initial dataset from file or session
        dataset = loadDataSet(request, inputParams, firstTime)

        # Load the requested table (or the first if no specified)
        table = loadTable(request, dataset, inputParams)

        # Load columns configuration. How to display columns and attributes (visible, render, editable)  
        loadColumnsConfig(request, dataset, table, inputParams, extraParams, firstTime)

        volPath, _stats, _imageDimensions, volOld = setRenderingOptions(request, dataset, table, inputParams)
        inputParams['volOld'] = volOld

        # Store variables into session
        storeToSession(request, inputParams, dataset, _imageDimensions)
    else:
        inputParams[sj.COLS_CONFIG] = None
        volPath = inputParams[sj.PATH]

    labelsToRender = getRenderableColumnsFromParams(extraParams, table)
    context, return_page = createContextShowj(request, inputParams, dataset, table, _stats, volPath, labelsToRender)

    render_var = render_to_response(return_page, RequestContext(request, context))

    # =TIME CONTROL==============================================================
    #    print "FINISH SHOWJ: ", datetime.now()-start
    # ===========================================================================

    return render_var


def cleanSession(request, filename):
    """ Clean data stored in session for a new visualization. """
    if filename in request.session:
        del request.session[filename]


def storeToSession(request, inputParams, dataset, _imageDimensions):
    # Store some parameters into session variable 
    datasetDict = {}
    datasetDict[sj.DATASET] = dataset
    datasetDict[sj.LABEL_SELECTED] = inputParams[sj.LABEL_SELECTED]
    datasetDict[sj.TABLE_NAME] = inputParams[sj.TABLE_NAME]
    datasetDict[sj.IMG_DIMS] = _imageDimensions

    request.session[inputParams[sj.PATH]] = datasetDict


def createContextShowj(request, inputParams, dataset, table, paramStats, volPath=None, labelsToRender=None):
    showjForm = ShowjForm(dataset,
                          inputParams[sj.COLS_CONFIG], labelsToRender,
                          inputParams)  # A form bound for the POST data and unbound for the GET

    if showjForm.is_valid() is False:
        print showjForm.errors

    context = createContext(dataset, table, inputParams[sj.COLS_CONFIG], request, showjForm, inputParams)

    if inputParams[sj.MODE] == sj.MODE_VOL_NGL:
        context.update(create_context_volume(request, inputParams, volPath, paramStats))

    elif inputParams[sj.MODE] == sj.MODE_GALLERY or inputParams[sj.MODE] == sj.MODE_TABLE:
        context.update({"showj_alt_js": getResourceJs('showj_' + inputParams[sj.MODE] + '_utils')})

    elif inputParams[sj.MODE] == 'column':
        context.update({"showj_alt_js": getResourceJs('showj_' + sj.MODE_TABLE + '_utils')})

    # IMPROVE TO KEEP THE ITEMS (SELECTED, ENABLED, CHANGES)
    context.update({sj.SELECTEDITEMS: inputParams[sj.SELECTEDITEMS],
                    sj.ENABLEDITEMS: inputParams[sj.ENABLEDITEMS],
                    sj.CHANGES: inputParams[sj.CHANGES],
                    })

    return_page = 'showj/%s%s%s' % ('showj_', showjForm.data[sj.MODE], '.html')
    return context, return_page


def createContext(dataset, table, columnsConfig, request, showjForm, inputParams):
    # Create context to be send

    context = {sj.IMG_DIMS: request.session[inputParams[sj.PATH]].get(sj.IMG_DIMS, 0),
               sj.IMG_ZOOM_DEFAULT: request.session.get(sj.IMG_ZOOM_DEFAULT, 0),
               # NOt used?: 23-12-2015. sj.PROJECT_NAME: request.session[sj.PROJECT_NAME],
               'form': showjForm}

    if dataset is not None:
        context.update({sj.DATASET: dataset})
    if columnsConfig is not None:
        context.update({sj.COLS_CONFIG: json.dumps({'columnsLayout': columnsConfig._columnsDict,
                                                    'colsOrder': inputParams[sj.ORDER],
                                                    'colsSortby': inputParams[sj.SORT_BY]
                                                    },
                                                   ensure_ascii=False,
                                                   cls=ColumnPropertiesEncoder)})
    if table is not None:
        context.update({'tableDataset': table})

    # showj_base context
    context = base_showj(request, context)
    context.update(context)

    return context


def getExtraParameters(extraParams, table):
    defaultColumnsLayoutProperties = {}
    _mapCol = {}
    _mapRender = {}
    enc_visible = False
    enc_render = False

    if extraParams is not None and extraParams != {}:
        for k in table.iterColumns():
            defaultColumnsLayoutProperties[k.getLabel()] = {}
            _mapCol[k.getLabel()] = k.getName()
            _mapRender[k.getLabel()] = k.getRenderType()

        for key, value in extraParams.iteritems():
            if key in {sj.RENDER, sj.VISIBLE}:

                if key == sj.VISIBLE:
                    val = {key: 'True'}
                    if not enc_visible:
                        enc_visible = True

                elif key == sj.RENDER:
                    val = {'renderable': 'True'}
                    if not enc_render:
                        enc_render = True

                params = value.split()
                for label in params:
                    if label in _mapCol and table.hasColumn(_mapCol[label]):
                        defaultColumnsLayoutProperties[label].update(val)

        if enc_visible or enc_render:
            for x in defaultColumnsLayoutProperties:
                if enc_visible:
                    if not 'visible' in defaultColumnsLayoutProperties[x]:
                        defaultColumnsLayoutProperties[x].update({sj.VISIBLE: 'False'})
                if enc_render:
                    # COL_RENDER_IMAGE = 3
                    if _mapRender[x] == 3 and not 'renderable' in defaultColumnsLayoutProperties[x]:
                        defaultColumnsLayoutProperties[x].update({'renderable': 'False'})
    return defaultColumnsLayoutProperties, _mapCol


# Load an Xmipp Dataset
def loadDatasetXmipp(path):
    """ Create a table from a metadata. """
    if path.endswith('.sqlite'):
        from pyworkflow.dataset import SqliteDataSet
        return SqliteDataSet(path)

    if path.endswith('.vol') or path.endswith('mrc'):
        from pyworkflow.dataset import SingleFileDataSet
        return SingleFileDataSet(path)

    from pyworkflow.em.packages.xmipp3 import XmippDataSet
    return XmippDataSet(str(path))


def testingSSH(request):
    context = {}
    # return render_to_response("testing_ssh.html", RequestContext(request, context))
    return render_to_response("scipion.html", RequestContext(request, context))


def volumeToNGL(volPath):
    """ We need an mrc map to be loaded into the ngl viewer"""
    from pyworkflow.em.convert import ImageHandler

    # return getResource('reference.mrc')

    # Clean volPath in case it comes with :mrc, ...
    nglVolume = volPath.split(":")[0]

    # If it ends in mrc
    if nglVolume.endswith(".mrc"):
        return nglVolume
    else:
        # Add mrc
        nglVolume += ".mrc"

    # If the ngl volume already exists
    if os.path.exists(nglVolume):
        return nglVolume

    else:
        # Convert input volumes
        ih = ImageHandler()

        ih.convert(volPath, nglVolume)

    return nglVolume


def create_context_volume(request, inputParams, volPath, param_stats):
    import os

    context = None

    if inputParams[sj.MODE] == sj.MODE_VOL_NGL:

        # We need to convert the map to a valid NGL density format (mrc)
        volPath = volumeToNGL(volPath)

        context = {"ngl": getResourceJs('ngl'),
                   "volPath": volPath,
                   "threshold": 1.5,
                   'minSigma': 0,
                   'maxSigma': 4,
                   "jquery_ui_css": getResourceCss("jquery_ui")
        }

    return context


def updateSessionTable(request):
    label = request.GET.get('label', None)
    type = request.GET.get('type', None)
    option = request.GET.get('option', None)

    cols_config = request.session[sj.COLS_CONFIG]

    if type == "renderable":
        cols_config.configColumn(label, renderable=option)
    elif type == "editable":
        cols_config.configColumn(label, editable=option)
    #    elif type == 'visible':
    #        cols_config.configColumn(label, visible=option)

    return HttpResponse(content_type='application/javascript')
