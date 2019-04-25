from PyQt5 import QtWidgets

from .pageids import PageID
from .simtype_ui import Ui_WizardPage


class SimTypePage(QtWidgets.QWizardPage, Ui_WizardPage):
    pageID=PageID.Type
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, WizardPage):
        super().setupUi(WizardPage)
        self.registerField('typeIsEM', self.typeEnergyMinimizationRadioButton)
        self.registerField('typeIsNVT', self.typeNVTRadioButton)
        self.registerField('typeIsNPT', self.typeNPTRadioButton)
        self.registerField('timeUnit', self.timeUnitComboBox)

    def nextId(self):
        if self.field('typeIsEM'):
            return PageID.EM
        else:
            return PageID.Integrator

    def timeUnit(self):
        return self.timeUnitComboBox.currentText()
