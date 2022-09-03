from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QTableWidgetItem
from data_manager import DataManager
import sys

db = None

class FindDialog(QtWidgets.QDialog):
    def __init__(self, findCallback, parent=None):
        super(FindDialog, self).__init__(parent)
        uic.loadUi('find.ui', self)
        self.resultCallback = findCallback

        self.setSearchKeyAction = QtWidgets.QAction("Find Record", self)
        self.setSearchKeyAction.setShortcut('return')
        self.setSearchKeyAction.triggered.connect(self.setSearchKey)
        self.addAction(self.setSearchKeyAction)

        self.show()

    def setSearchKey(self):
        self.resultCallback(self.SearchBox.text())
        self.accept()

class IndexDialog(QtWidgets.QDialog):
    def __init__(self, resultCallback, parent=None):
        super(IndexDialog, self).__init__(parent)
        uic.loadUi('indexes.ui', self)
        self.resultCallback = resultCallback

        self.ByTitleButton.clicked.connect(self.setByTitle)
        self.ByRecordNumberButton.clicked.connect(self.setByRecordID)

        self.setRecordIDIndexAction = QtWidgets.QAction("Set RecordID Index", self)
        self.setRecordIDIndexAction.setShortcut('a')
        self.setRecordIDIndexAction.triggered.connect(self.setByRecordID)
        self.addAction(self.setRecordIDIndexAction)

        self.setTitleIndexAction = QtWidgets.QAction("Set Title Index", self)
        self.setTitleIndexAction.setShortcut('b')
        self.setTitleIndexAction.triggered.connect(self.setByTitle)
        self.addAction(self.setTitleIndexAction)

        self.show()

    def setByTitle(self):
        self.resultCallback("TITLE")
        self.accept()

    def setByRecordID(self):
        self.resultCallback("RecordID")
        self.accept()

class BrowseWindow(QtWidgets.QMainWindow):
    def __init__(self):
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

        self.browseTable.setCurrentCell(db.getCurrentRecord()["RecordID"]-1, 0)


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('main.ui', self) # Load the .ui file
        self.updateView()
        self.currentIndex = "RecordID"
        self.NextButton.clicked.connect(self.nextRecord)
        self.PreviousButton.clicked.connect(self.previousRecord)
        self.IndexButton.clicked.connect(self.openIndexDialog)

        self.nextRecordAction = QtWidgets.QAction("Next Record", self)
        self.nextRecordAction.setShortcut('down')
        self.nextRecordAction.triggered.connect(self.nextRecord)
        self.addAction(self.nextRecordAction)

        self.previousRecordAction = QtWidgets.QAction("Previous Record", self)
        self.previousRecordAction.setShortcut('up')
        self.previousRecordAction.triggered.connect(self.previousRecord)
        self.addAction(self.previousRecordAction)

        self.changeIndexAction = QtWidgets.QAction("Index Menu", self)
        self.changeIndexAction .setShortcut('i')
        self.changeIndexAction.triggered.connect(self.openIndexDialog)
        self.addAction(self.changeIndexAction)

        self.findAction = QtWidgets.QAction("Find Menu", self)
        self.findAction .setShortcut('f')
        self.findAction.triggered.connect(self.openFindDialog)
        self.FindButton.clicked.connect(self.openFindDialog)
        self.addAction(self.findAction)

        self.browseAction = QtWidgets.QAction("Browse Window", self)
        self.browseAction .setShortcut('f')
        self.browseAction.triggered.connect(self.openBrowseWindow)
        self.BrowseButton.clicked.connect(self.openBrowseWindow)
        self.addAction(self.browseAction)

        self.makeSaleAction = QtWidgets.QAction("Make Sale", self)
        self.makeSaleAction .setShortcut('s')
        self.makeSaleAction.triggered.connect(self.makeSale)
        self.addAction(self.makeSaleAction)

        self.show() # Show the GUI

    def updateView(self):
        self.titleValue.setText(db.getCurrentRecord()["TITLE"])
        self.authorValue.setText(db.getCurrentRecord()["AUTHORLAST"])
        self.recordIDValue.setText(str(db.getCurrentRecord()["RecordID"]))
        self.maxDesiredValue.setText(str(db.getCurrentRecord()["MxNumber"]))
        self.toOrderValue.setText(str(db.getCurrentRecord()["NumberSold"]))
        self.lastSaleValue.setText(str(db.getCurrentRecord()["LstSaleDate"]))
        self.historyValue.setText(str(db.getCurrentRecord()["SalesHist"]))


    def makeSale(self):
        db.makeSale()
        self.updateView()

    def nextRecord(self):
        db.nextRecord()
        self.updateView()

    def previousRecord(self):
        db.previousRecord()
        self.updateView()

    def setIndex(self, index):
        db.changeIndex(index)
        self.updateView()

    def openIndexDialog(self):
        dlg = IndexDialog(self.setIndex, self)
        dlg.show()

    def findRecord(self, search):
        self.setIndex("TITLE")
        db.search(search)
        self.updateView()

    def openFindDialog(self):
        dlg = FindDialog(self.findRecord, self)
        dlg.show()

    def openBrowseWindow(self):
        self.browse = BrowseWindow()
        self.browse.show()

if __name__ == '__main__':
    #db = DataManager(r"F:\alpha4v8\BookInv\BOOKINV.DBF")
    db = DataManager(r"bookinv.db")
    #db.convertDB()
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()

