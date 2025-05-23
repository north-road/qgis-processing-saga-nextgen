"""
***************************************************************************
    SplitRGBBands.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
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

import os

from processing.tools.system import getTempFilename
from qgis.core import (
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterRasterDestination,
)

from processing_saga_nextgen.processing.utils import SagaUtils
from .SagaAlgorithmBase import SagaAlgorithmBase

pluginPath = os.path.normpath(
    os.path.join(os.path.split(os.path.dirname(__file__))[0], os.pardir)
)


class SplitRGBBands(SagaAlgorithmBase):
    """
    Split RGB Bands algorithm
    """

    INPUT = "INPUT"
    R = "R"
    G = "G"
    B = "B"

    # pylint:disable=missing-function-docstring

    def initAlgorithm(self, config=None):  # pylint: disable=unused-argument
        self.addParameter(
            QgsProcessingParameterRasterLayer(self.INPUT, self.tr("Input layer"))
        )

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.R, self.tr("Output R band layer")
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.G, self.tr("Output G band layer")
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.B, self.tr("Output B band layer")
            )
        )

    def name(self):
        return "splitrgbbands"

    def displayName(self):
        return self.tr("Split RGB bands")

    def group(self):
        return self.tr("Raster tools")

    def groupId(self):
        return "rastertools"

    def processAlgorithm(self, parameters, context, feedback):  # pylint:disable=too-many-locals
        # TODO: check correct num of bands
        inLayer = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        input_file = inLayer.source()
        temp = getTempFilename(None).replace(".", "")
        basename = os.path.basename(temp)
        validChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        safeBasename = "".join(c for c in basename if c in validChars)
        temp = os.path.join(os.path.dirname(temp), safeBasename)

        r = self.parameterAsOutputLayer(parameters, self.R, context)
        g = self.parameterAsOutputLayer(parameters, self.G, context)
        b = self.parameterAsOutputLayer(parameters, self.B, context)

        commands = []
        trailing = ""
        lib = ""
        commands.append('%sio_gdal 0 -GRIDS "%s" -FILES "%s"' % (lib, temp, input_file))
        commands.append(
            '%sio_gdal 1 -GRIDS "%s_%s1.sgrd" -FORMAT 1 -TYPE 0 -FILE "%s"'
            % (lib, temp, trailing, r)
        )
        commands.append(
            '%sio_gdal 1 -GRIDS "%s_%s2.sgrd" -FORMAT 1 -TYPE 0 -FILE "%s"'
            % (lib, temp, trailing, g)
        )
        commands.append(
            '%sio_gdal 1 -GRIDS "%s_%s3.sgrd" -FORMAT 1 -TYPE 0 -FILE "%s"'
            % (lib, temp, trailing, b)
        )

        SagaUtils.createSagaBatchJobFileFromSagaCommands(commands)
        SagaUtils.executeSaga(feedback)

        return {self.R: r, self.G: g, self.B: b}
