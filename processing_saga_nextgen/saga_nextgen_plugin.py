"""QGIS Processing R Provider

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import os
from qgis.PyQt.QtCore import QTranslator, QCoreApplication
from qgis.core import QgsApplication
from qgis.gui import QgisInterface
from processing_saga_nextgen.processing.provider import SagaNextGenAlgorithmProvider


class SagaNextGenProviderPlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface: QgisInterface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        super().__init__()
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QgsApplication.locale()
        locale_path = os.path.join(self.plugin_dir, "i18n", "{}.qm".format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.provider = None

    @staticmethod
    def tr(message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("SagaNextGenProvider", message)

    def initProcessing(self):
        """Create the Processing provider"""
        self.provider = SagaNextGenAlgorithmProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        """Creates application GUI widgets"""
        self.initProcessing()

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        QgsApplication.processingRegistry().removeProvider(self.provider)
