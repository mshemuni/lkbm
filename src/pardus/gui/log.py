# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'log.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FormLog(object):
    def setupUi(self, FormLog):
        FormLog.setObjectName("FormLog")
        FormLog.resize(432, 497)
        self.gridLayout = QtWidgets.QGridLayout(FormLog)
        self.gridLayout.setObjectName("gridLayout")
        self.tableWidget = QtWidgets.QTableWidget(FormLog)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)

        self.retranslateUi(FormLog)
        QtCore.QMetaObject.connectSlotsByName(FormLog)

    def retranslateUi(self, FormLog):
        _translate = QtCore.QCoreApplication.translate
        FormLog.setWindowTitle(_translate("FormLog", "Log"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("FormLog", "Address"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("FormLog", "Time"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("FormLog", "Domain"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("FormLog", "Message"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    FormLog = QtWidgets.QWidget()
    ui = Ui_FormLog()
    ui.setupUi(FormLog)
    FormLog.show()
    sys.exit(app.exec_())
