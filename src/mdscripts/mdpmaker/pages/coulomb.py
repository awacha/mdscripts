from PyQt5 import QtWidgets

from .base import PageID, PageBase
from .coulomb_ui import Ui_WizardPage


class CoulombPage(QtWidgets.QWizardPage, Ui_WizardPage, PageBase):
    pageID = PageID.Coulomb

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, WizardPage):
        super().setupUi(WizardPage)
        self.registerField('coulombtype', self.coulombtypeComboBox)
        self.registerField('coulomb-modifier', self.coulomb_modifierComboBox)
        self.registerField(
            'rcoulomb-switch', self.rcoulomb_switchDoubleSpinBox)
        self.registerField('rcoulomb', self.rcoulombDoubleSpinBox)
        self.registerField('epsilon_r', self.epsilon_rDoubleSpinBox)
        self.registerField('epsilon_rf', self.epsilon_rfDoubleSpinBox)
        self.coulombtypeComboBox.currentIndexChanged.connect(
            self.onTypeModified)
        self.coulomb_modifierComboBox.currentIndexChanged.connect(
            self.onTypeModified)
        self.onTypeModified()

    def nextId(self):
        return PageID.VdW

    def onTypeModified(self):
        # ToDo
        pass
