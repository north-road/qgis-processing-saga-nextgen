"""
Test saga utils
"""

from unittest import TestCase

from processing_saga_nextgen.processing.utils import SagaUtils


class UtilTests(TestCase):
    """
    Test saga utils
    """

    def test_make_path_safe(self):
        """
        Test SagaUtils.make_path_safe
        """
        path = r"C:\Users\fclementi\AppData\Roaming\QGIS\QGIS3\profiles\new(profile)\processing\saga_batch_job.bat"
        expected = r'"C:\Users\fclementi\AppData\Roaming\QGIS\QGIS3\profiles\new^(profile^)\processing\saga_batch_job.bat"'
        self.assertEqual(expected, SagaUtils.make_path_safe(path))
