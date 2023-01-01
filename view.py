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
        self.add_qt_action("Set AuthorLast Index", self.set_by_authorlast, 'c', self.ByAuthorLastButton)
        self.add_qt_action("Set Subj+Title Index", self.set_by_subjtitle, 'd', self.BySubjTitleButton)
        self.add_qt_action("Set Pub+Title Index", self.set_by_pubtitle, 'e', self.ByPubTitleButton)
        self.add_qt_action("Set OrderActiv Index", self.set_by_orderactiv, 'f', self.ByOrderActivButton)
        self.add_qt_action("Set ISBN Index", self.set_by_isbn, 'g', self.ByISBNButton)
        self.show()

    def set_by_title(self):
        self.resultCallback("Title")
        self.accept()

    def set_by_record_id(self):
        self.resultCallback("RecordID")
        self.accept()

    def set_by_authorlast(self):
        self.resultCallback("AuthorLast")
        self.accept()

    def set_by_subjtitle(self):
        self.resultCallback("Subj+Title")
        self.accept()

    def set_by_pubtitle(self):
        self.resultCallback("Pub+Title")
        self.accept()

    def set_by_orderactiv(self):
        self.resultCallback("OrderActiv")
        self.accept()

    def set_by_isbn(self):
        self.resultCallback("ISBN")
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
            self.browseTable.setItem(i, 0, QTableWidgetItem(record["Title"]))
            self.browseTable.setItem(i, 1, QTableWidgetItem(record["AuthorLast"]))
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
        self.add_qt_action("Delete", self.delete_record, '', self.DeleteButton)
        self.add_qt_action("Make Sale", self.make_sale, 's')

        self.browse = None
        self.enter_window = None
        self.update_view()
        self.show()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self.enter_window is None:
            self.main_win.show()
        event.accept()

    def pretty_bool(self, inval):
        if inval is None:
            inval = ""
        elif inval == 1:
            inval = "y"
        else:
            inval = "n"
        return inval

    def pretty_int(self, inval):
        if inval is None:
            return ""
        return str(inval)

    def update_view(self):
        record = self.db.get_current_record()
        self.titleValue.setText(record["Title"])
        self.authorValue.setText(record["AuthorLast"])
        self.ISBNValue.setText(record["ISBN"])
        self.recordIDValue.setText(str(record["RecordID"]))
        self.maxDesiredValue.setText(self.pretty_int(record["MxNumber"]))
        self.toOrderValue.setText(self.pretty_int(record["NumberSold"]))
        self.lastSaleValue.setText(record["LstSaleDate"])
        self.historyValue.setText(record["SalesHist"])
        self.orderStatusValue.setText(record["OrderActiv"])
        self.SubjectValue.setText(record["Subj"])
        self.AcqDateValue.setText(record["AcquisDate"])
        price = record["Price"]
        if price is not None:
            price = "%.2f" % price
        else:
            price = ""
        self.PriceValue.setText(price)
        self.PublisherValueLabel.setText(record["Pub"])
        self.IngOValue.setText(self.pretty_bool(record["IngO"]))
        self.IngTValue.setText(self.pretty_bool(record["IngT"]))
        self.IPSValue.setText(self.pretty_bool(record["IPS"]))
        self.POValue.setText(record["PoNum"])
        self.PrevPOValue.setText(record["PrevPoNum"])
        self.OnOrderValue.setText(self.pretty_int(record["NumOnOrder"]))
        self.BOValue.setText(self.pretty_int(record["BoNumber"]))
        if self.browse is not None:
            self.browse.update_selected()

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
        self.set_index("Title")
        self.db.search(search)
        self.update_view()

    def delete_record(self):
        confirm = QtWidgets.QMessageBox
        ret = confirm.question(self, 'Delete Confirmation', f"Are you sure? This will delete the record.", confirm.Yes | confirm.No)
        if ret == confirm.Yes:
            self.db.delete_current_record()
            self.update_view()

    def open_find_dialog(self):
        dlg = FindDialog(self.find_record, self)
        dlg.show()

    def open_browse_window(self):
        if self.browse == None:
            self.browse = BrowseWindow(self.db, self)
        self.browse.update_selected()
        self.browse.show()
        self.browse.activateWindow()

    def open_enter_window(self):
        self.browse = None
        self.enter_window = EnterWindow(self.db, self)
        self.close()