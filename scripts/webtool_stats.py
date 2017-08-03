#!/usr/bin/env python
# **************************************************************************
# *
# * Authors:     Pablo Conesa (pconesa@cnb.csic.es)
# *
# * Unidad de Bioinformatica of Centro Nacional de Biotecnologia, CSIC
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

import sys, os
from pyworkflow.manager import Manager


def usage(error):
    print """
    ERROR: %s
    
    Usage: scipion python scripts/webtool_stats.py [SCIPION_USER_DATA] [yyyy]
        Collects stats for the projects 
        Optional to pass SCIPION_USER_DATA folder from which to read 'projects'.
        Optional restrict actions to projects created in a certain year
    """ % error
    sys.exit(1)    

n = len(sys.argv)

print n , sys.argv

if n > 3:
    usage("Incorrect number of input parameters")

# Default values    
year = None
customUserData = os.environ['SCIPION_USER_DATA']
for i in range(n-1):
    arg = sys.argv[i+1]
    print arg
    if arg.isdigit():
        year = int(arg)
    else:
        customUserData = arg

print "Loading projects from:\n", customUserData, " for year " , year 
 
# Create a new project
manager = Manager(SCIPION_USER_DATA=customUserData)

for projInfo in manager.listProjects():
    projName = projInfo.getName()
    proj = manager.loadProject(projName)

    creationTime = proj.getCreationTime()
    creationYear = creationTime.year

    if year is None or creationYear == year:

	for prot in proj.getRuns():
            print "\t".join([projName , str(creationTime), prot._label, str(prot.numberOfSteps), prot.getStatus()])



