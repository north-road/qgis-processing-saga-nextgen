"""
***************************************************************************
    supervisedclassification.py
    ---------------------
    Date                 : July 2013
    Copyright            : (C) 2013 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from processing.tests.TestData import table


def editCommands(commands):
    """
    Returns the edit commands
    """
    commands[-3] = commands[-3] + " -STATS " + table()
    return commands
