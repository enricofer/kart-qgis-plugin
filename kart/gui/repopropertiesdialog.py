import os

from qgis.core import Qgis
from qgis.utils import iface
from qgis.gui import QgsMessageBar

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QSizePolicy


from kart.layers import LayerTracker
from kart.kartapi import executeskart
from kart.gui.extentselectionpanel import ExtentSelectionPanel

WIDGET, BASE = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "repopropertiesdialog.ui")
)


class RepoPropertiesDialog(BASE, WIDGET):
    def __init__(self, repo):
        super(QDialog, self).__init__(iface.mainWindow())
        self.setupUi(self)

        self.repo = repo

        self.bar = QgsMessageBar()
        self.bar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout().addWidget(self.bar)

        self.buttonBox.accepted.connect(self.okClicked)
        self.buttonBox.rejected.connect(self.reject)

        self.chkShowBoundingBox.stateChanged.connect(self.showBoundingBoxStateChanged)

        self.extentPanel = ExtentSelectionPanel(self)
        self.grpFilter.layout().addWidget(self.extentPanel)

        self.populate()

    @executeskart
    def populate(self):
        self.txtTitle.setText(self.repo.title())
        self.labelRepoLocation.setText(os.path.normpath(self.repo.path))
        self.labelWorkingCopyLocation.setText(self.repo.workingCopyLocation())
        self.btnColor.setColor(self.repo.boundingBoxColor)
        self.chkShowBoundingBox.setChecked(self.repo.showBoundingBox)
        self.btnColor.setEnabled(self.repo.showBoundingBox)
        spatialFilter = self.repo.spatialFilter()
        if spatialFilter is not None:
            self.grpFilter.setChecked(True)
            self.extentPanel.setValueFromRect(spatialFilter)
        else:
            self.grpFilter.setChecked(False)

    @executeskart
    def okClicked(self):
        self.repo.setTitle(self.txtTitle.text())
        self.repo.boundingBoxColor = self.btnColor.color()
        self.repo.showBoundingBox = self.chkShowBoundingBox.isChecked()
        if self.grpFilter.isChecked():
            extent = self.extentPanel.getExtent()
            if extent is None:
                self.bar.pushMessage("Invalid extent value", Qgis.Warning, duration=5)
                return
        else:
            extent = None
        self.repo.setSpatialFilter(extent)
        LayerTracker.instance().updateRubberBandsForRepo(self.repo)
        self.accept()

    def showBoundingBoxStateChanged(self, _):
        self.btnColor.setEnabled(self.chkShowBoundingBox.isChecked())
