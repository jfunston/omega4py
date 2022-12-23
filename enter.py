from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView
from util import ui_methods

@ui_methods
class EnterWindow(QtWidgets.QMainWindow):
    def __init__(self, db, view_window):
        self.db = db
        self.view_window = view_window

        super(EnterWindow, self).__init__()
        uic.loadUi("enter.ui", self)

        self.add_qt_action("Save", self.save_record, 'f10', self.SaveButton)

        self.allLabels = []
        self.allLabels.append(self.titleValue)
        self.allLabels.append(self.authorValue)
        self.allLabels.append(self.ISBNValue)
        self.allLabels.append(self.recordIDValue)
        self.allLabels.append(self.maxDesiredValue)
        self.allLabels.append(self.toOrderValue)
        self.allLabels.append(self.lastSaleValue)
        self.allLabels.append(self.historyValue)
        self.allLabels.append(self.orderStatusValue)
        self.allLabels.append(self.SubjectValue)
        self.allLabels.append(self.AcqDateValue)
        self.allLabels.append(self.PriceValue)
        self.allLabels.append(self.PublisherValue)
        self.allLabels.append(self.IngOValue)
        self.allLabels.append(self.IngTValue)
        self.allLabels.append(self.IPSValue)
        self.allLabels.append(self.POValue)
        self.allLabels.append(self.PrevPOValue)
        self.allLabels.append(self.OnOrderValue)
        self.allLabels.append(self.BOValue)

        defaultStyle = self.recordIDValue.styleSheet()
        for label in self.allLabels:
            label.setStyleSheet("background-color: lightblue; border: 1px solid black;")
            label.setText("")
        self.recordIDValue.setStyleSheet(defaultStyle)

        self.recordID = self.db.get_max_record_id() + 1
        self.recordIDValue.setText(str(self.recordID))
        self.show()

    def save_record(self):
        record = {}
        record["Title"] = self.titleValue.text()
        record["AuthorLast"] = self.authorValue.text()
        record["ISBN"] = self.ISBNValue.toPlainText()
        self.db.insert_record(record)
        self.view_window.set_index("RecordID")
        self.db.set_current_id(len(self.db.records)-1)
        self.view_window.update_view()
        self.view_window.show()
        self.close()

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        geo = self.geometry()
        geo.moveCenter(self.view_window.geometry().center())
        self.setGeometry(geo)