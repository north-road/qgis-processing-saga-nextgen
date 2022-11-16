from ..processing.utils import makePathSafe
from unittest import TestCase


class UtilTests(TestCase):
    def test_makePathSafe(self):
        path = r"C:\Users\fclementi\AppData\Roaming\QGIS\QGIS3\profiles\new(profile)\processing\saga_batch_job.bat"
        expected = r'"C:\Users\fclementi\AppData\Roaming\QGIS\QGIS3\profiles\new^(profile^)\processing\saga_batch_job.bat"'
        assert expected == makePathSafe(path)
