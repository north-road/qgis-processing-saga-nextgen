"""
Test running SAGA algorithms
"""

import os
import shutil
import tempfile

from qgis.core import (
    QgsProcessingParameterNumber,
    QgsProcessingParameterDefinition,
    QgsVectorLayer,
    QgsApplication,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsProcessingContext,
    QgsProject,
    QgsProcessingFeedback,
)
from qgis.testing import start_app, unittest

from .AlgorithmsTestBase import AlgorithmsTest
from ..processing.SagaParameters import Parameters, SagaImageOutputParam
from ..processing.provider import SagaNextGenAlgorithmProvider


class TestSagaAlgorithms(unittest.TestCase, AlgorithmsTest):
    """
    Test running SAGA algorithms
    """

    # pylint: disable=missing-function-docstring

    @classmethod
    def setUpClass(cls):
        start_app()
        cls.provider = SagaNextGenAlgorithmProvider()
        QgsApplication.processingRegistry().addProvider(cls.provider)
        cls.cleanup_paths = []

        cls.temp_dir = tempfile.mkdtemp()
        cls.cleanup_paths.append(cls.temp_dir)

    @classmethod
    def tearDownClass(cls):
        QgsApplication.processingRegistry().removeProvider(cls.provider)
        for path in cls.cleanup_paths:
            shutil.rmtree(path)

    def definition_file(self):
        return "saga_algorithm_tests.yaml"

    def test_is_parameter_line(self):
        # Test determining whether a line is a parameter line
        self.assertFalse(Parameters.is_parameter_line(""))
        self.assertFalse(Parameters.is_parameter_line("xxxxxxxxx"))
        self.assertTrue(
            Parameters.is_parameter_line(
                "QgsProcessingParameterNumber|R_PERCTL_MIN|Percentiles Range for RED max|QgsProcessingParameterNumber.Integer|1|False|1|99"
            )
        )
        self.assertTrue(
            Parameters.is_parameter_line(
                "*QgsProcessingParameterNumber|R_PERCTL_MIN|Percentiles Range for RED max|QgsProcessingParameterNumber.Integer|1|False|1|99"
            )
        )
        self.assertTrue(Parameters.is_parameter_line("SagaImageOutput|RGB|Output RGB"))

    def test_param_line(self):
        # Test creating a parameter from a description line
        param = Parameters.create_parameter_from_line(
            "QgsProcessingParameterNumber|R_PERCTL_MIN|Percentiles Range for RED max|QgsProcessingParameterNumber.Integer|1|False|1|99"
        )
        self.assertIsInstance(param, QgsProcessingParameterNumber)
        self.assertEqual(param.name(), "R_PERCTL_MIN")
        self.assertEqual(param.description(), "Percentiles Range for RED max")
        self.assertEqual(param.dataType(), QgsProcessingParameterNumber.Type.Integer)
        self.assertFalse(
            param.flags() & QgsProcessingParameterDefinition.Flag.FlagOptional
        )
        self.assertEqual(param.minimum(), 1)
        self.assertEqual(param.maximum(), 99)

        # Test SagaImageOutputParam line
        param = Parameters.create_parameter_from_line("SagaImageOutput|RGB|Output RGB")
        self.assertIsInstance(param, SagaImageOutputParam)
        self.assertEqual(param.name(), "RGB")
        self.assertEqual(param.description(), "Output RGB")
        self.assertEqual(param.defaultFileExtension(), "tif")
        self.assertEqual(param.supportedOutputRasterLayerExtensions(), ["tif"])

    def test_non_ascii_output(self):
        # create a memory layer and add to project and context
        layer = QgsVectorLayer(
            "Point?crs=epsg:3857&field=fldtxt:string&field=fldint:integer",
            "testmem",
            "memory",
        )
        self.assertTrue(layer.isValid())
        pr = layer.dataProvider()
        f = QgsFeature()
        f.setAttributes(["test", 123])
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(100, 200)))
        f2 = QgsFeature()
        f2.setAttributes(["test2", 457])
        f2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(110, 200)))
        self.assertTrue(pr.addFeatures([f, f2]))
        self.assertEqual(layer.featureCount(), 2)
        QgsProject.instance().addMapLayer(layer)
        context = QgsProcessingContext()
        context.setProject(QgsProject.instance())

        alg = QgsApplication.processingRegistry().createAlgorithmById(
            "sagang:featuresbuffer"
        )
        self.assertIsNotNone(alg)

        temp_file = os.path.join(self.temp_dir, "non_ascii_ñññ.shp")
        parameters = {
            "SHAPES": "testmem",
            "DIST_FIELD_DEFAULT": 5,
            "NZONES": 1,
            "DARC": 5,
            "DISSOLVE": False,
            "POLY_INNER": False,
            "BUFFER": temp_file,
        }
        feedback = QgsProcessingFeedback()

        _, ok = alg.run(parameters, context, feedback)
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(temp_file))

        # make sure that layer has correct features
        res = QgsVectorLayer(temp_file, "res")
        self.assertTrue(res.isValid())
        self.assertEqual(res.featureCount(), 2)

        QgsProject.instance().removeMapLayer(layer)


if __name__ == "__main__":
    unittest.main()
