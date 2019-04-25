from PyQt5 import QtWidgets

from .base import PageID, PageBase
from .vdw_ui import Ui_WizardPage


class VdWPage(QtWidgets.QWizardPage, Ui_WizardPage, PageBase):
    pageID = PageID.VdW

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, WizardPage):
        super().setupUi(WizardPage)
        self.registerField('vdwtype', self.vdwtypeComboBox)
        self.registerField('vdw-modifier', self.vdw_modifierComboBox)
        self.registerField(
            'rvdw-switch', self.rvdw_switchDoubleSpinBox)
        self.registerField('rvdw', self.rvdwDoubleSpinBox)
        self.registerField('dispcorr', self.dispcorrComboBox)
        self.vdwtypeComboBox.currentIndexChanged.connect(
            self.onTypeModified)
        self.vdw_modifierComboBox.currentIndexChanged.connect(
            self.onTypeModified)
        self.onTypeModified()

    def nextId(self):
        return PageID.Ewald

    def onTypeModified(self):
        # ToDo
        pass
