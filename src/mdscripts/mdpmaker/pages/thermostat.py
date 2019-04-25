from PyQt5 import QtWidgets

from .base import PageID, PageBase
from .thermostat_ui import Ui_WizardPage


class ThermostatPage(QtWidgets.QWizardPage, Ui_WizardPage, PageBase):
    pageID = PageID.Thermostat

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, WizardPage):
        super().setupUi(WizardPage)

    def nextId(self):
        if self.wizard().field('typeIsNPT'):
            return PageID.Barostat
        else:
            return PageID.End
