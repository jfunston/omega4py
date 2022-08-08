from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from data_manager import DataManager
import sys

db = None

class IndexDialog(QtWidgets.QDialog):
    def __init__(self, resultCallback, parent=None):
        super(IndexDialog, self).__init__(parent)
        uic.loadUi('indexes.ui', self)
        self.resultCallback = resultCallback

        self.ByTitleButton.clicked.connect(self.setByTitle)

        self.show()

    def setByTitle(self):
        self.resultCallback("Title")
        self.accept()

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

        self.show() # Show the GUI

    def updateView(self):
        self.titleValue.setText(db.getCurrentRecord()["TITLE"])
        self.authorValue.setText(db.getCurrentRecord()["AUTHORLAST"])

    def nextRecord(self):
        db.nextRecord()
        self.updateView()

    def previousRecord(self):
        db.previousRecord()
        self.updateView()

    def setIndex(self, index):
        self.currentIndex = index

    def openIndexDialog(self):
        dlg = IndexDialog(self.setIndex, self)
        dlg.show()

if __name__ == '__main__':
    #db = DataManager(r"F:\alpha4v8\BookInv\BOOKINV.DBF")
    db = DataManager(r"bookinv.db")
    #db.convertDB()
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()

