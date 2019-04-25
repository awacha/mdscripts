from PyQt5 import QtWidgets

from .base import PageID, PageBase
from .neighboursearch_ui import Ui_WizardPage


class NeighbourSearchPage(QtWidgets.QWizardPage, Ui_WizardPage, PageBase):
    pageID=PageID.Neighboursearch
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, WizardPage):
        super().setupUi(WizardPage)
        self.registerField('cutoff-scheme', self.cutoff_schemeComboBox)
        self.registerField('nstlist', self.nstlistSpinBox)
        self.registerField('ns-type', self.ns_typeComboBox)
        self.registerField('pbc', self.pbcComboBox)
        self.registerField('verlet-buffer-tolerance', self.verlet_buffer_toleranceDoubleSpinBox)
        self.registerField('rlist', self.rlistDoubleSpinBox)
        self.nstlistSpinBox.valueChanged.connect(self.updateTimeLabels)

    def nextId(self):
        return PageID.Freqcontrol

    def updateTimeLabels(self):
        self.nstListTimeLabel.setText('{:.6f} {}'.format(self.timeStep()*self.nstlistSpinBox.value(), self.timeUnit()))
