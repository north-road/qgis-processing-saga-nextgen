"""
Processing provider for SAGA
"""

import os

from processing.core.ProcessingConfig import ProcessingConfig, Setting
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (Qgis,
                       QgsProcessingProvider,
                       QgsMessageLog)

from processing_saga_nextgen.gui.gui_utils import GuiUtils
from processing_saga_nextgen.processing.utils import SagaUtils
from .SagaAlgorithm import SagaAlgorithm
from .SplitRGBBands import SplitRGBBands


class SagaNextGenAlgorithmProvider(QgsProcessingProvider):
    """
    Processing provider for SAGA
    """

    def __init__(self):
        super().__init__()
        self.algs = []

    def load(self):  # pylint:disable=missing-docstring
        ProcessingConfig.settingIcons["SAGANG"] = self.icon()
        ProcessingConfig.addSetting(Setting("SAGANG",
                                            SagaUtils.SAGA_IMPORT_EXPORT_OPTIMIZATION,
                                            self.tr('Enable SAGA Import/Export optimizations'), False))
        ProcessingConfig.addSetting(Setting("SAGANG",
                                            SagaUtils.SAGA_FOLDER, self.tr('SAGA folder'),
                                            '',
                                            valuetype=Setting.FOLDER))
        ProcessingConfig.addSetting(Setting("SAGANG",
                                            SagaUtils.SAGA_LOG_COMMANDS,
                                            self.tr('Log execution commands'), True))
        ProcessingConfig.addSetting(Setting("SAGANG",
                                            SagaUtils.SAGA_LOG_CONSOLE,
                                            self.tr('Log console output'), True))
        ProcessingConfig.readSettings()
        self.refreshAlgorithms()
        return True

    def unload(self):  # pylint:disable=missing-docstring
        ProcessingConfig.removeSetting(SagaUtils.SAGA_LOG_CONSOLE)
        ProcessingConfig.removeSetting(SagaUtils.SAGA_LOG_COMMANDS)
        ProcessingConfig.removeSetting(SagaUtils.SAGA_FOLDER)

    def loadAlgorithms(self):  # pylint:disable=missing-docstring
        version = SagaUtils.getInstalledVersion(True)
        if version is None:
            QgsMessageLog.logMessage(
                self.tr('Problem with SAGA installation: SAGA was not found or is not correctly installed'),
                self.tr('Processing'), Qgis.Critical)
            return

        if version < SagaUtils.REQUIRED_VERSION:
            QgsMessageLog.logMessage(
                self.tr('Problem with SAGA installation: unsupported SAGA version (found: {}, required: >={}).').format(
                    version, SagaUtils.REQUIRED_VERSION),
                self.tr('Processing'),
                Qgis.Critical)

        self.algs = []
        folder = SagaUtils.sagaDescriptionPath()
        for descriptionFile in os.listdir(folder):
            if descriptionFile.endswith('txt'):
                try:
                    alg = SagaAlgorithm(os.path.join(folder, descriptionFile))
                    if alg.name().strip() != '':
                        self.algs.append(alg)
                    else:
                        QgsMessageLog.logMessage(self.tr('Could not open SAGA algorithm: {}'.format(descriptionFile)),
                                                 self.tr('Processing'), Qgis.Critical)
                except Exception as e:  # pylint: disable=broad-except
                    QgsMessageLog.logMessage(
                        self.tr('Could not open SAGA algorithm: {}\n{}'.format(descriptionFile, str(e))),
                        self.tr('Processing'), Qgis.Critical)

        self.algs.append(SplitRGBBands())
        for a in self.algs:
            self.addAlgorithm(a)

    def name(self):
        """
        Display name for provider
        """
        return 'SAGA Next Gen'

    def longName(self):
        """
        Display long name for provider
        """
        version = SagaUtils.getInstalledVersion()
        return 'SAGA Next Gen ({})'.format(version) if version is not None else 'SAGA'

    def id(self):
        """
        Unique ID for provider
        """
        return 'sagang'

    def versionInfo(self):
        """
        Provider plugin version
        """
        return "1.0.0"

    def defaultVectorFileExtension(self, hasGeometry=True):
        """
        Default extension -- we use shapefile for spatial layers, dbf for non-spatial layers
        """
        return 'shp' if hasGeometry else 'dbf'

    def defaultRasterFileExtension(self):
        """
        Default extension -- only sdat supported
        """
        return 'sdat'

    def supportedOutputRasterLayerExtensions(self):
        """
        Only sdat supported
        """
        return ['sdat']

    def supportedOutputVectorLayerExtensions(self):
        """
        Only shapefile supported
        """

        return ['shp', 'dbf']

    def supportedOutputTableExtensions(self):
        """
        Only dbf supported
        """
        return ['dbf']

    def supportsNonFileBasedOutput(self):
        """
        SAGA Provider doesn't support non file based outputs
        """
        return False

    def icon(self):
        """
        Returns the provider's icon
        """
        return GuiUtils.get_icon("providerSaga.svg")

    def svgIconPath(self):
        """
        Returns a path to the provider's icon as a SVG file
        """
        return GuiUtils.get_icon_svg("providerSaga.svg")

    def tr(self, string, context=''):
        """
        Translates a string
        """
        if context == '':
            context = 'SagaNgAlgorithmProvider'
        return QCoreApplication.translate(context, string)
