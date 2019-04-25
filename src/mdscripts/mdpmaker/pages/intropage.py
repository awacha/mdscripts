from PyQt5 import QtWidgets

from .intropage_ui import Ui_WizardPage
from .pageids import PageID


class IntroPage(QtWidgets.QWizardPage, Ui_WizardPage):
    pageID=PageID.Intro
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, WizardPage):
        super().setupUi(WizardPage)
        self.registerField('consent*', self.consentCheckBox)

    def nextId(self):
        return PageID.Type
