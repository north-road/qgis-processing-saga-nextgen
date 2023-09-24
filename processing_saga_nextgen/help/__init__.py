"""
Help utilities
"""
import codecs
import os
import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    import yaml

from qgis.core import QgsSettings, Qgis
from qgis.PyQt.QtCore import QLocale, QCoreApplication


def loadShortHelp():
    """
    Load short help descriptions
    """
    h = {}
    path = os.path.dirname(__file__)
    for f in os.listdir(path):
        if f.endswith("yaml"):
            filename = os.path.join(path, f)
            with codecs.open(filename, encoding='utf-8') as stream:
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore",
                                            category=DeprecationWarning)
                    for k, v in yaml.load(stream,
                                          Loader=yaml.SafeLoader).items():
                        if v is None:
                            continue
                        h[k] = QCoreApplication.translate(
                            "{}Algorithm".format(f[:-5].upper()), v)

    version = ".".join(Qgis.QGIS_VERSION.split(".")[0:2])
    overrideLocale = QgsSettings().value('locale/overrideFlag', False, bool)
    if not overrideLocale:
        locale = QLocale.system().name()[:2]
    else:
        locale = QgsSettings().value('locale/userLocale', '')
    locale = locale.split("_")[0]

    def replace(s):
        if s is not None:
            return s.replace("{qgisdocs}",
                             "https://docs.qgis.org/%s/%s/docs" % (
                             version, locale))

        return None

    h = {k: replace(v) for k, v in list(h.items())}

    return h


shortHelp = loadShortHelp()
