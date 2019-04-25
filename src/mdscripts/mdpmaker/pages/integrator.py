from PyQt5 import QtWidgets

from .base import PageID, PageBase
from .integrator_ui import Ui_WizardPage


class IntegratorPage(QtWidgets.QWizardPage, Ui_WizardPage, PageBase):
    pageID=PageID.Integrator
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def calcTimeStep(self) -> float:
        w=self.wizard()
        assert isinstance(w, QtWidgets.QWizard)
        tu = self.timeUnit()
        dt=self.timeStepDoubleSpinBox.value()
        if tu=='fs':
            return dt*1e3
        elif tu=='ps':
            return dt
        elif tu=='ns':
            return dt/1e3
        elif tu=='ms':
            return dt/1e6
        else:
            raise ValueError(tu)

    def setupUi(self, WizardPage):
        super().setupUi(WizardPage)
        self.registerField('dt', self.timeStepDoubleSpinBox)
        self.registerField('nsteps', self.nstepsSpinBox)
        self.registerField('comm-mode', self.commTypeComboBox)
        self.registerField('comm-grps', self.commGrpsLineEdit)
        self.registerField('nstcomm', self.nstcommSpinBox)
        self.timeStepDoubleSpinBox.valueChanged.connect(self.updateTimeLabels)
        self.nstepsSpinBox.valueChanged.connect(self.updateTimeLabels)
        self.nstcommSpinBox.valueChanged.connect(self.updateTimeLabels)

    def nextId(self):
        return PageID.Neighboursearch

    def updateTimeLabels(self):
        self.nstepsTimeLabel.setText('{:.6f} {}'.format(self.timeStep()*self.nstepsSpinBox.value(), self.timeUnit()))
        self.nstcommTimeLabel.setText('{:.6f} {}'.format(self.timeStep()*self.nstcommSpinBox.value(), self.timeUnit()))
        self.timeStepTimeLabel.setText('{:.6f} {}'.format(self.timeStep(), self.timeUnit()))
