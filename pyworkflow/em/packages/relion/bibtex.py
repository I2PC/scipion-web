# coding: latin-1
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
Bibtex string file for Relion protocols.
"""

_bibtexStr = """

@article{Scheres2012a,
title = "A Bayesian View on Cryo-EM Structure Determination ",
journal = "JMB",
volume = "415",
number = "2",
pages = "406 - 418",
year = "2012",
issn = "0022-2836",
doi = "http://dx.doi.org/10.1016/j.jmb.2011.11.010",
url = "http://www.sciencedirect.com/science/article/pii/S0022283611012290",
author = "Scheres, Sjors H.W.",
keywords = "cryo-electron microscopy, three-dimensional reconstruction, maximum a posteriori estimation "
}

@article{Scheres2012b,
title = "RELION: Implementation of a Bayesian approach to cryo-EM structure determination ",
journal = "JSB",
volume = "180",
number = "3",
pages = "519 - 530",
year = "2012",
issn = "1047-8477",
doi = "http://dx.doi.org/10.1016/j.jsb.2012.09.006",
url = "http://www.sciencedirect.com/science/article/pii/S1047847712002481",
author = "Scheres, Sjors H.W.",
keywords = "Electron microscopy, Single-particle analysis, Maximum likelihood, Image processing, Software development "
}

@article{Chen2012,
title = "Prevention of overfitting in cryo-EM structure determination",
journal = "Nat. Meth.",
volume = "9",
number = "3",
pages = "853 - 854",
year = "2012",
doi = "http://dx.doi.org/10.1038/nmeth.2115",
author = "Chen, Shaoxia and Scheres, Sjors H.W.",
}

"""

from pyworkflow.utils import parseBibTex

_bibtex = parseBibTex(_bibtexStr)  
