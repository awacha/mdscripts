from PyQt5 import QtWidgets

from .pages import IntroPage, EMPage, SimTypePage, IntegratorPage, \
    NeighbourSearchPage, FreqControlPage, CoulombPage, \
    VdWPage, EwaldPage, ThermostatPage, EndPage


class MDPWizard(QtWidgets.QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pages = []
        self.setupUi(self)

    def setupUi(self, Wizard):
        self.setButtonText(QtWidgets.QWizard.CustomButton1, 'Load MDP...')
        self.customButtonClicked.connect(self.onCustomButtonClicked)
        for pageclass in [
             IntroPage, SimTypePage, EMPage, IntegratorPage,
             NeighbourSearchPage,
             FreqControlPage, CoulombPage, VdWPage, EwaldPage,
             ThermostatPage, EndPage]:
            page = pageclass()
            self._pages.append(page)
            self.setPage(page.pageID, page)

    def onCustomButtonClicked(self, which: int):
        if which == QtWidgets.QWizard.CustomButton1:
            # open new file
            filename, fltr = QtWidgets.QFileDialog.getOpenFileUrl(
                parent=self, caption='Load an MDP file', directory='',
                filter='MDP files (*.mdp);;All files (*)',
                initialFilter='MDP files (*.mdp)')
            if filename:
                self.loadMDP(filename)

    def loadMDP(filename):
        pass

    def saveMDP(filename):
        pass
