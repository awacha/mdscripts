# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/mdscripts/mdpmaker/pages/intropage.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        WizardPage.setObjectName("WizardPage")
        WizardPage.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(WizardPage)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(WizardPage)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.consentCheckBox = QtWidgets.QCheckBox(WizardPage)
        self.consentCheckBox.setObjectName("consentCheckBox")
        self.verticalLayout.addWidget(self.consentCheckBox)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        _translate = QtCore.QCoreApplication.translate
        WizardPage.setWindowTitle(_translate("WizardPage", "WizardPage"))
        WizardPage.setTitle(_translate("WizardPage", "Welcome"))
        self.label.setText(_translate("WizardPage", "<html><head/><body><p>With this wizard you can construct an MDP file for GROMACS.</p><p>Please note that:</p><ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This is not (and is not meant to be) a generally applicable tool, i.e. not all possible MDP options are exposed. If you consider doing anything special (which you might certainly do), you must edit the resulting MDP file to your needs.</li><li style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This is only an aid for constructing the files. You should have a deep understanding of MD simulations and GROMACS, in particular. All the responsibility is yours, therefore you must check the resulting MDP file for correctness. The author should not be held liable for incorrect simulation results!</li></ul><p>If you are in doubt of a setting, please check the official GROMACS documentation at <a href=\"https://manual.gromacs.org/documentation/current/user-guide/mdp-options.html\"><span style=\" text-decoration: underline; color:#2980b9;\">https://manual.gromacs.org/documentation/current/user-guide/mdp-options.html</span></a></p></body></html>"))
        self.consentCheckBox.setText(_translate("WizardPage", "I\'m aware of my responsibilities"))

