from PyQt5 import QtWidgets

from .pageids import PageID


class EndPage(QtWidgets.QWizardPage):
    pageID = PageID.End

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, WizardPage):
        self.setTitle('Finish')
        self.setSubTitle('Please select a file to save your MDP file...')
        self.filesel = QtWidgets.QFileDialog(self)
        self.vboxlayout = QtWidgets.QVBoxLayout(self)
        self.vboxlayout.addWidget(self.filesel)
        self.filesel.show()
