from PyQt5 import QtWidgets

from .em_ui import Ui_WizardPage
from .pageids import PageID


class EMPage(QtWidgets.QWizardPage, Ui_WizardPage):
    pageID=PageID.EM
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, WizardPage):
        super().setupUi(WizardPage)
        self.registerField('emIntegrator', self.emIntegratorComboBox)
        self.registerField('emtol', self.emToleranceDoubleSpinBox)
        self.registerField('emstep', self.emNstepsSpinBox)
        self.registerField('nstcgsteep', self.emnstcgsteepSpinBox)
        self.registerField('nbfgscorr', self.emnbfgscorrSpinBox)
        self.registerField('emnsteps', self.emNstepsSpinBox)
        self.emIntegratorComboBox.currentIndexChanged.connect(self.onIntegratorChanged)
        self.onIntegratorChanged()

    def nextId(self):
        return PageID.Freqcontrol

    def onIntegratorChanged(self):
        self.emnstcgsteepSpinBox.setEnabled(self.emIntegratorComboBox.currentText()=='cg')
        self.emnbfgscorrSpinBox.setEnabled(self.emIntegratorComboBox.currentText()=='l-bfgs')
