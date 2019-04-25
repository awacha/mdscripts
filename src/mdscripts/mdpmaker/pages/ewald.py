from PyQt5 import QtWidgets

from .base import PageID, PageBase
from .ewald_ui import Ui_WizardPage


class EwaldPage(QtWidgets.QWizardPage, Ui_WizardPage, PageBase):
    pageID = PageID.Ewald

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, WizardPage):
        super().setupUi(WizardPage)
        self.registerField('fourierspacing', self.fourierspacingDoubleSpinBox)
        self.registerField('pme-order', self.pme_orderSpinBox)
        self.registerField(
            'constraints', self.constraintsComboBox)
        self.registerField('lincs_order', self.lincs_orderSpinBox)
        self.registerField('lincs_iter', self.lincs_iterSpinBox)
        self.registerField(
            'lincs_warnangle', self.lincs_warnangleDoubleSpinBox)

    def nextId(self):
        if (self.wizard().field('typeIsNVT') or self.wizard().field('typeIsNPT')):
            return PageID.Thermostat
        else:
            return PageID.End
