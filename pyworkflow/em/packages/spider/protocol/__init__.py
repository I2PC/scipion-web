# **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (jmdelarosa@cnb.csic.es)
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
"""
Import of all protocols included in spider.
"""
from protocol_base import SpiderProtocol
from protocol_classify_base import SpiderProtClassify
from protocol_filters import SpiderProtFilter
from protocol_align_apsr import SpiderProtAlignAPSR
from protocol_custommask import SpiderProtCustomMask
from protocol_ca_pca import SpiderProtCAPCA
from protocol_classify_diday import SpiderProtClassifyDiday
from protocol_classify_ward import SpiderProtClassifyWard
from protocol_classify_kmeans import SpiderProtClassifyKmeans
from protocol_align_pairwise import SpiderProtAlignPairwise

from protocol_projmatch import SpiderProtRefinement
from protocol_reconstruct import SpiderProtReconstruct

# Spider workflow is not working yet
# (well, any workflow now)
#from protocol_mda import SpiderWfMDA


