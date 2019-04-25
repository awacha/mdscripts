from PyQt5 import QtWidgets

from .pageids import PageID


class PageBase:
    def timeUnit(self):
        w=self.wizard()
        assert isinstance(w, QtWidgets.QWizard)
        return w.page(PageID.Type).timeUnit()

    def timeStep(self):
        return self.wizard().page(PageID.Integrator).calcTimeStep()

    def showEvent(self, event):
        print('ShowEvent')
        try:
            self.updateTimeLabels()
        except AttributeError:
            pass
