from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView
from util import ui_methods
from enter import EnterWindow


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
class IndexDialog(QtWidgets.QDialog):
    def __init__(self, resultCallback, parent=None):
        super(IndexDialog, self).__init__(parent)
        uic.loadUi('indexes.ui', self)

        self.resultCallback = resultCallback
        self.add_qt_action("Set RecordID Index", self.set_by_record_id, 'a', self.ByRecordNumberButton)
        self.add_qt_action("Set Title Index", self.set_by_title, 'b', self.ByTitleButton)
        self.show()

    def set_by_title(self):
        self.resultCallback("TITLE")
        self.accept()

    def set_by_record_id(self):
        self.resultCallback("RecordID")
        self.accept()


@ui_methods
class BrowseWindow(QtWidgets.QMainWindow):
    def __init__(self, db, view):
        self.db = db
        self.view = view

        super(BrowseWindow, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('browse.ui', self) # Load the .ui file
        self.browseTable.setRowCount(len(db.records))
        i = 0
        for record in db.records:
            self.browseTable.setItem(i, 0, QTableWidgetItem(record["TITLE"]))
            self.browseTable.setItem(i, 1, QTableWidgetItem(record["AUTHORLAST"]))
            self.browseTable.setItem(i, 2, QTableWidgetItem(record["Subj"]))
            self.browseTable.setItem(i, 3, QTableWidgetItem(str(record["Price"])))
            i += 1
        self.browseTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.browseTable.verticalHeader().setVisible(False)
        self.update_selected()

        self.add_qt_action("Close", self.close, 'escape')
        self.add_qt_action("Select", self.user_select, 'return')

    def update_selected(self):
        self.browseTable.setFocus()
        self.browseTable.selectRow(self.db.get_current_id())

    def user_select(self):
        self.db.set_current_id(self.browseTable.currentRow())
        self.view.update_view()
        self.close()


@ui_methods
class ViewWindow(QtWidgets.QMainWindow):
    def __init__(self, db, main_win):
        self.db = db
        self.main_win = main_win

        super(ViewWindow, self).__init__()
        uic.loadUi('view.ui', self)

        self.add_qt_action("Next Record", self.next_record, 'down', self.NextButton)
        self.add_qt_action("Previous Record", self.previous_record, 'up', self.PreviousButton)
        self.add_qt_action("Index Menu", self.open_index_dialog, 'i', self.IndexButton)
        self.add_qt_action("Find Menu", self.open_find_dialog, 'f', self.FindButton)
        self.add_qt_action("Browse Window", self.open_browse_window, 'b', self.BrowseButton)
        #self.add_qt_action("Change", self.change_window, 'c', self.ChangeButton)
        self.add_qt_action("Enter", self.open_enter_window, 'e', self.EnterButton)
        self.add_qt_action("Make Sale", self.make_sale, 's')

        self.browse = None
        self.enter_window = None
        self.update_view()
        self.show()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self.enter_window is None:
            self.main_win.show()
        event.accept()

    def update_view(self):
        self.titleValue.setText(self.db.get_current_record()["TITLE"])
        self.authorValue.setText(self.db.get_current_record()["AUTHORLAST"])
        self.ISBNValue.setText(self.db.get_current_record()["ISBN"])
        self.recordIDValue.setText(str(self.db.get_current_record()["RecordID"]))
        self.maxDesiredValue.setText(str(self.db.get_current_record()["MxNumber"]))
        self.toOrderValue.setText(str(self.db.get_current_record()["NumberSold"]))
        self.lastSaleValue.setText(str(self.db.get_current_record()["LstSaleDate"]))
        self.historyValue.setText(str(self.db.get_current_record()["SalesHist"]))
        self.orderStatusValue.setText(self.db.get_current_record()["OrderActiv"])

    def make_sale(self):
        self.db.make_sale()
        self.update_view()

    def next_record(self):
        self.db.next_record()
        self.update_view()

    def previous_record(self):
        self.db.previous_record()
        self.update_view()

    def set_index(self, index):
        self.db.change_index(index)
        self.browse = None
        self.update_view()

    def open_index_dialog(self):
        dlg = IndexDialog(self.set_index, self)
        dlg.show()

    def find_record(self, search):
        self.set_index("TITLE")
        self.db.search(search)
        self.update_view()

    def open_find_dialog(self):
        dlg = FindDialog(self.find_record, self)
        dlg.show()

    def open_browse_window(self):
        if self.browse == None:
            self.browse = BrowseWindow()
        self.browse.update_selected()
        self.browse.show()
        self.browse.activateWindow()

    def open_enter_window(self):
        self.browse = None
        self.enter_window = EnterWindow(self.db, self)
        self.close()