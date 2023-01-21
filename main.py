import os
import shutil

from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QFileDialog
from data_manager import DataManager
from dbfread import DBF
import sys

from util import ui_methods
from view import ViewWindow

main_win = None
db = None


@ui_methods
class SearchListDialog(QtWidgets.QDialog):
    def __init__(self, findCallback, db, parent=None):
        super(SearchListDialog, self).__init__(parent)
        uic.loadUi('search.ui', self)
        self.db = db

        self.setWindowTitle("Search/List")
        self.resultCallback = findCallback
        self.add_qt_action("Find Record", self.set_search_key, 'return')
        self.findBox.setFocus()
        self.show()

    def set_search_key(self):
        self.db.substring_search(self.fieldComboBox.currentText(), self.findBox.text(), self.orderComboBox.currentText())
        self.resultCallback()
        self.accept()

@ui_methods
class FindReplaceDialog(QtWidgets.QDialog):
    def __init__(self, db, parent=None):
        super(FindReplaceDialog, self).__init__(parent)
        uic.loadUi('replace.ui', self)
        self.setWindowTitle("Find -> Replace")
        self.db = db

        self.add_qt_action("Find Replace", self.find_replace, 'return')
        self.findBox.setFocus()
        self.show()

    def find_replace(self):
        changed = self.db.count_search(self.fieldComboBox.currentText(), self.findBox.text())
        confirm = QtWidgets.QMessageBox
        ret = confirm.question(self, 'Search Replace Confirmation', f"Are you sure? This will affect {changed} record(s).", confirm.Yes | confirm.No)
        if ret == confirm.Yes:
            self.db.find_replace(self.fieldComboBox.currentText(), self.findBox.text(), self.replaceBox.text())
        self.accept()

@ui_methods
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, db):
        self.db = db
        self.view = None

        super(MainWindow, self).__init__()
        uic.loadUi('main.ui', self)

        self.setWindowTitle("Omega4")
        self.currentIndex = "RecordID"
        self.add_qt_action("View Records", self.view_records, 'v', self.ViewButton)
        self.add_qt_action("Search Records", self.search_records, 's', self.SearchButton)
        self.add_qt_action("List Non-Empty Order Code", self.ordercode_nonempty, '', self.ListNonEmptyOrderButton)
        self.add_qt_action("Find Replace", self.find_replace, '', self.FindReplaceButton)
        self.actionLoad_A4_DB.triggered.connect(self.load_a4_db)
        self.actionSave_Backup.triggered.connect(self.save_backup)
        self.actionLoad_Backup.triggered.connect(self.load_backup)

        self.update_view()
        self.show()

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        self.update_view()
        event.accept()

    def update_view(self):
        self.recordsInDBValue.setText(str(self.db.get_total_records()))
        self.recordsInListValue.setText(str(len(self.db.records)))

    def load_a4_db(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select A4 DBF file", "", "DBF Files (*.DBF)")
        if file_name is None or file_name == "":
            return
        self.db.table = DBF(file_name, load=True)
        self.db.convert_db()
        self.db = DataManager(r"bookinv.db")
        self.update_view()

    def save_backup(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Select DB backup file name", "", "SQLite DB Files (*.db)")
        if file_name is None or file_name == "" or file_name.find("bookinv.db") != -1:
            return
        if len(file_name.split('.')) == 1 or file_name.split('.')[1] != "db":
            file_name += ".db"
        shutil.copyfile("bookinv.db", file_name)

    def load_backup(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select DB file name", "", "SQLite DB Files (*.db)")
        if file_name is None or file_name == "" or file_name.find("bookinv.db") != -1:
            return
        shutil.copyfile(file_name, "bookinv.db")
        self.db = DataManager(r"bookinv.db")
        self.update_view()

    def view_records(self):
        if len(self.db.records) == 0:
            confirm = QtWidgets.QMessageBox
            ret = confirm.question(self, 'Reset Search', "There are no records to view. Do you want to reset the search/list?", confirm.Yes | confirm.No)
            if ret == confirm.Yes:
                self.db.substring_search("Title", "", "Title")
                self.update_view()
            else:
                return

        self.view = ViewWindow(self.db, self)
        self.view.show()
        self.close()

    def search_callback(self, searchKey):
        self.db.substring_search(searchKey)
        self.update_view()

    def ordercode_nonempty(self):
        self.db.ordercode_search()
        self.update_view()

    def search_records(self):
        find = SearchListDialog(lambda : self.update_view(), self.db, self)
        find.show()

    def find_replace(self):
        shutil.copyfile("bookinv.db", "find_replace_backup.db")
        replace = FindReplaceDialog(self.db, self)
        replace.show()


if __name__ == '__main__':
    db = DataManager(r"bookinv.db")
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    main_win = MainWindow(db)
    app.exec_()