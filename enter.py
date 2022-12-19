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

        self.recordID = self.db.get_max_record_id() + 1
        self.recordIDValue.setText(str(self.recordID))
        self.show()

    def save_record(self):
        record = {}
        record["Title"] = self.titleEdit.toPlainText()
        record["AuthorLast"] = self.authorEdit.toPlainText()
        record["ISBN"] = self.ISBNEdit.toPlainText()
        self.db.insert_record(record)
        self.view_window.set_index("RecordID")
        # TODO max+1 of RecordID
        self.db.set_current_id(len(self.db.records)-1)
        self.view_window.update_view()
        self.view_window.show()
        self.close()