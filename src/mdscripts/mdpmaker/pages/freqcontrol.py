from PyQt5 import QtWidgets

from .base import PageID, PageBase
from .freqcontrol_ui import Ui_WizardPage


class FreqControlPage(QtWidgets.QWizardPage, Ui_WizardPage, PageBase):
    pageID = PageID.Freqcontrol

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, WizardPage):
        super().setupUi(WizardPage)
        self.registerField('nstxout', self.nstxoutSpinBox)
        self.registerField('nstvout', self.nstvoutSpinBox)
        self.registerField('nstfout', self.nstfoutSpinBox)
        self.registerField('nstlog', self.nstlogSpinBox)
        self.registerField('nstenergy', self.nstenergySpinBox)
        self.registerField('nstcalcenergy', self.nstcalcenergySpinBox)
        self.registerField(
            'nstxout-compressed', self.nstxout_compressedSpinBox)
        self.registerField(
            'compressed-x-precision', self.compressed_x_precisionDoubleSpinBox)
        self.registerField('compressed-x-grps', self.compressed_x_grpsLineEdit)
        self.nstxoutSpinBox.valueChanged.connect(self.updateTimeLabels)
        self.nstvoutSpinBox.valueChanged.connect(self.updateTimeLabels)
        self.nstfoutSpinBox.valueChanged.connect(self.updateTimeLabels)
        self.nstlogSpinBox.valueChanged.connect(self.updateTimeLabels)
        self.nstenergySpinBox.valueChanged.connect(self.updateTimeLabels)
        self.nstcalcenergySpinBox.valueChanged.connect(self.updateTimeLabels)
        self.nstxout_compressedSpinBox.valueChanged.connect(
            self.updateTimeLabels)

    def nextId(self):
        return PageID.Coulomb

    def updateTimeLabels(self):
        for spinbox, label in [
            (self.nstxoutSpinBox, self.nstxoutTimeLabel),
            (self.nstvoutSpinBox, self.nstvoutTimeLabel),
            (self.nstfoutSpinBox, self.nstfoutTimeLabel),
            (self.nstlogSpinBox, self.nstlogTimeLabel),
            (self.nstenergySpinBox, self.nstenergyTimeLabel),
            (self.nstcalcenergySpinBox, self.nstcalcenergyTimeLabel),
            (self.nstxout_compressedSpinBox, self.nstxout_compressedTimeLabel),
             ]:
            label.setText('{:.6f} {}'.format(
                self.timeStep()*spinbox.value(), self.timeUnit()))
