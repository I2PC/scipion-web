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
This modules contains constants related to Spider protocols
"""

#------------------ Constants values --------------------------------------
# spider documentation url
SPIDER_DOCS = 'http://spider.wadsworth.org/spider_doc/spider/docs/man/'

# Filter types
FILTER_TOPHAT = 0
FILTER_SPACE_REAL = 1
FILTER_FERMI = 2
FILTER_BUTTERWORTH = 3
FILTER_RAISEDCOS = 4

FILTER_LOWPASS = 0
FILTER_HIGHPASS = 1

# CA-PCA protocol
CA = 0
PCA = 1
IPCA = 2

# Center of gravity values
CG_NONE = 0
CG_PH = 1
CG_RT180 = 2

