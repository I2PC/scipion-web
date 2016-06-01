# **************************************************************************
# *
# * Authors:    Jose Gutierrez (jose.gutierrez@cnb.csic.es)
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
from os.path import basename
import xmipp

from pyworkflow.em.wizard import EmWizard
from django.shortcuts import render_to_response
from django.http import HttpResponse

from pyworkflow.em.packages.resmap.wizard import ResmapPrewhitenWizard, INSTRUCTIONS
from pyworkflow.web.app.em_wizard import *
from tools import *
from pyworkflow.web.app.views_base import base_wiz
from pyworkflow.web.app.views_util import savePlot, loadProject, getResourceCss, getResourceJs
from pyworkflow.gui.plotter import Plotter
from pyworkflow.em.packages.resmap import ProtResMap
from pyworkflow.em.packages.resmap.wizard import myCreatePrewhiteningFigure


class ResmapPrewhitenWizardWeb(ResmapPrewhitenWizard):
    _environments = [WEB_DJANGO]

    def _run(self, protocol, request):

        if not protocol.useSplitVolume:
            emptyInput = protocol.inputVolume.pointsNone()
        else:
            emptyInput = (protocol.volumeHalf1.pointsNone() or
                          protocol.volumeHalf2.pointsNone())

        if emptyInput:
            return HttpResponse("Error: select the input volume(s) first.")
        else:
            plotUrl, min_ang = getPlotResMap(request, protocol)

            ang = protocol.prewhitenAng.get()
            if ang < min_ang:
                ang = min_ang

            context = {
                       # Params
                       'ang': round(ang, 2),
                       'ramp': protocol.prewhitenRamp.get(),
                       # Extra Params
                       'pValue': protocol.pVal.get(),
                       'minRes': protocol.minRes.get(),
                       'maxRes': protocol.maxRes.get(),
                       'stepRes': protocol.stepRes.get(),
                       # Others
                       'plot': plotUrl,
                       'min_ang': round(min_ang, 2),
                       'messi_js': getResourceJs('messi'),
                       'messi_css': getResourceCss('messi'),
                       }

            if protocol.useSplitVolume:
                context.update({'useSplit': 1,
                                'inputId': protocol.volumeHalf1.getUniqueId(),
                                'splitId': protocol.volumeHalf2.getUniqueId()
                                })
            else:
                context.update({'inputId': protocol.inputVolume.getUniqueId()
                                })

            if protocol.applyMask:
                if protocol.maskVolume.pointsNone():
                    return HttpResponse("Error: select the input mask first.")
                context.update({'useMask': 1,
                                'maskId': protocol.maskVolume.getUniqueId()
                                })

            context = base_wiz(request, context)
            return render_to_response('wizards/wiz_resmap.html', context)

#===============================================================================
# RESMAP REQUEST UPDATE
#===============================================================================

def get_resmap_plot(request):
    # LOAD Project
    project = loadProject(request)

    # Create protocol
    newProtocol = project.newProtocol(ProtResMap)

    # GET and SET Parameters
    newAng = request.GET.get('ang')
    newProtocol.prewhitenAng.set(float(newAng))

    newRamp = request.GET.get('ramp')
    newProtocol.prewhitenRamp.set(float(newRamp))

    def setPointerValue(inputPointer, uniqueIdKey):
        uniqueId = request.GET.get(uniqueIdKey)
        parts = uniqueId.split('.')
        inputPointer.set(project.mapper.selectById(parts[0]))
        inputPointer.setExtendedParts(parts[1:])

    useSplit = request.GET.get('useSplit', None) is not None
    newProtocol.useSplitVolume.set(useSplit)

    if not useSplit:
        setPointerValue(newProtocol.inputVolume, 'inputId')
    else:
        setPointerValue(newProtocol.volumeHalf1, 'inputId')
        setPointerValue(newProtocol.volumeHalf2, 'splitId')

    useMask = request.GET.get('useMask', None) is not None
    newProtocol.applyMask.set(useMask)

    if useMask:
        setPointerValue(newProtocol.maskVolume, 'maskId')

    # Extra Params
    pValue = request.GET.get('pValue', None)
    if pValue is not None:
        newProtocol.pVal.set(pValue)

    minRes = request.GET.get('minRes', None)
    if minRes is not None:
        newProtocol.minRes.set(minRes)

    maxRes = request.GET.get('maxRes', None)
    if maxRes is not None:
        newProtocol.maxRes.set(maxRes)

    stepRes = request.GET.get('stepRes', None)
    if stepRes is not None:
        newProtocol.stepRes.set(stepRes)

    plotUrl, _ = getPlotResMap(request, newProtocol)

    return HttpResponse(plotUrl, content_type='application/javascript')

#===============================================================================
# RESMAP UTILS 
#===============================================================================

def getPlotResMap(request, protocol):
     #1st step: Convert input volumes
    results = _beforePreWhitening(protocol, protocol._getTmpPath(abs=True, create=True))
    min_ang = 2.1* results['vxSize']
    #2nd step: Generate plot
    plotter = _runPreWhiteningWeb(protocol, results)
    #3rd step: Save to png image
    
#     plotUrl = "/" + savePlot(request, plotter)
    plotUrl = savePlot(request, plotter, close=True)
    return plotUrl, min_ang

def _beforePreWhitening(protocol, workingDir):
    from pyworkflow.em.convert import ImageHandler
    # Convert input volumes
    ih = ImageHandler()
    projPath = protocol.getProject().getPath()

    def convertVol(inputVol, outputFn):
        index, path = inputVol.get().getLocation()
        ih.convert((index, join(projPath, path)), join(workingDir, outputFn))

    if protocol.useSplitVolume:
        convertVol(protocol.volumeHalf1, 'volume1.map')
        convertVol(protocol.volumeHalf2, 'volume2.map')
    else:
        convertVol(protocol.inputVolume, 'volume1.map')

    return protocol.runResmap(workingDir, wizardMode=True)

     
def _runPreWhiteningWeb(protocol, results):
    
    newAng = protocol.prewhitenAng.get()
    newRamp = protocol.prewhitenRamp.get()
    
    figsize = (18, 9)
    gridsize = [0, 0]
    plotter = Plotter(*gridsize, figsize=figsize, windowTitle="ResMap")
    
    myCreatePrewhiteningFigure(results, plotter.getFigure(),
                             newAng, newRamp
                            )
    
    return plotter
