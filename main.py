from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QFileDialog
from data_manager import DataManager
from dbfread import DBF
import sys

from util import ui_methods
from view import ViewWindow

main_win = None
db = None


@ui_methods
class FindDialog(QtWidgets.QDialog):
    def __init__(self, findCallback, parent=None):
        super(FindDialog, self).__init__(parent)
        uic.loadUi('find.ui', self)

        self.resultCallback = findCallback
        self.add_qt_action("Find Record", self.set_search_key, 'return')
        self.show()

    def set_search_key(self):
        self.resultCallback(self.SearchBox.text())
        self.accept()


@ui_methods
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, db):
        self.db = db
        self.view = None

        super(MainWindow, self).__init__()
        uic.loadUi('main.ui', self)

        self.currentIndex = "RecordID"
        self.add_qt_action("View Records", self.view_records, 'v', self.ViewButton)
        self.add_qt_action("Search Records", self.search_records, 's', self.SearchButton)
        self.add_qt_action("List 200 Order Code", self.ordercode_200, '', self.List200Button)
        self.add_qt_action("List Non-Empty Order Code", self.ordercode_nonempty, '', self.ListNonEmptyOrderButton)
        self.add_qt_action("Load A4 DB", self.load_a4_db, 'l', self.LoadA4Button)

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
        self.db.table = DBF(file_name, load=True)
        self.db.convert_db()
        self.db = DataManager(r"bookinv.db")

    def view_records(self):
        self.view = ViewWindow(self.db, self)
        self.view.show()
        self.close()

    def search_callback(self, searchKey):
        self.db.substring_search(searchKey)
        self.update_view()

    def ordercode_200(self):
        self.db.ordercode_search("200")
        self.update_view()

    def ordercode_nonempty(self):
        self.db.ordercode_search("")
        self.update_view()

    def search_records(self):
        find = FindDialog(self.search_callback, self)
        find.show()


if __name__ == '__main__':
    db = DataManager(r"bookinv.db")
    app = QtWidgets.QApplication(sys.argv)
    main_win = MainWindow(db)
    app.exec_()