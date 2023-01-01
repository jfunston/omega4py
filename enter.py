from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView
from util import ui_methods, pretty_int, pretty_bool

@ui_methods
class EnterWindow(QtWidgets.QMainWindow):
    def __init__(self, db, view_window, in_record=None):
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
        self.allLabels.append(self.OrderStatusValue)
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

        default_style = self.recordIDValue.styleSheet()
        for label in self.allLabels:
            label.setStyleSheet("background-color: lightblue; border: 1px solid black;")
            try:
                label.setText("")
            except:
                label.setPlainText("")
        self.recordIDValue.setStyleSheet(default_style)

        self.edit_mode = False
        if in_record is None:
            self.recordID = self.db.get_max_record_id() + 1
        else:
            self.recordID = in_record["RecordID"]
            self.edit_mode = True
            self.update_fields(in_record)
        self.recordIDValue.setText(str(self.recordID))
        self.show()

    def update_fields(self, record):
        self.titleValue.setText(record["Title"])
        self.authorValue.setText(record["AuthorLast"])
        self.ISBNValue.setText(record["ISBN"])
        self.recordIDValue.setText(str(record["RecordID"]))
        self.maxDesiredValue.setText(pretty_int(record["MxNumber"]))
        self.toOrderValue.setText(pretty_int(record["NumberSold"]))
        self.lastSaleValue.setText(record["LstSaleDate"])
        self.historyValue.setPlainText(record["SalesHist"])
        self.OrderStatusValue.setText(record["OrderActiv"])
        self.SubjectValue.setText(record["Subj"])
        self.AcqDateValue.setText(record["AcquisDate"])
        price = record["Price"]
        if price is not None:
            price = "%.2f" % price
        else:
            price = ""
        self.PriceValue.setText(price)
        self.PublisherValue.setText(record["Pub"])
        self.IngOValue.setText(pretty_bool(record["IngO"]))
        self.IngTValue.setText(pretty_bool(record["IngT"]))
        self.IPSValue.setText(pretty_bool(record["IPS"]))
        self.POValue.setText(record["PoNum"])
        self.PrevPOValue.setText(record["PrevPoNum"])
        self.OnOrderValue.setText(pretty_int(record["NumOnOrder"]))
        self.BOValue.setText(pretty_int(record["BoNumber"]))

    def yn_to_int(self, value, value_name):
        if value == 'y' or value == 'Y' or value == '1':
            return 1
        elif value == 'n' or value == 'N' or value == '0':
            return 0
        elif value == "" or value is None:
            return None
        else:
            raise ValueError(f"Record not saved, {value_name} must be 'y', 'n', or empty")

    def to_float(self, value, value_name):
        converted = 0.0
        if value == "" or value is None:
            return None
        try:
            converted = float(value)
        except ValueError:
            raise ValueError(f"Record not saved, {value_name} must be a decimal value or empty")
        return converted

    def to_int(self, value, value_name):
        converted = 0
        if value == "" or value is None:
            return None
        try:
            converted = int(value)
        except ValueError:
            raise ValueError(f"Record not saved, {value_name} must be a number or empty")
        return converted

    def save_record(self):
        record = {}
        record["RecordID"] = self.recordID
        record["Title"] = self.titleValue.text()
        record["AuthorLast"] = self.authorValue.text()
        record["Pub"] = self.PublisherValue.text()
        record["AcquisDate"] = self.AcqDateValue.text()
        record["ISBN"] = self.ISBNValue.text()
        record["Subj"] = self.SubjectValue.text()
        record["LstSaleDate"] = self.lastSaleValue.text()
        record["PoNum"] = self.POValue.text()
        record["SalesHist"] = self.historyValue.toPlainText()
        record["OrderActiv"] = self.OrderStatusValue.text()
        record["PrevPoNum"] = self.PrevPOValue.text()
        try:
            record["MxNumber"] = self.to_int(self.maxDesiredValue.text(), "Max # Desired")
            record["NumberSold"] = self.to_int(self.toOrderValue.text(), "Number Sold")
            record["NumOnOrder"] = self.to_int(self.OnOrderValue.text(), "# on Order")
            record["BoNumber"] = self.to_int(self.BOValue.text(), "# BO'd")
            record["IPS"] = self.yn_to_int(self.IPSValue.text(), "IPS")
            record["IngO"] = self.yn_to_int(self.IngOValue.text(), "IngOR")
            record["IngT"] = self.yn_to_int(self.IngTValue.text(), "IngTN")
            record["Price"] = self.to_float(self.PriceValue.text(), "price")
        except ValueError as err:
            self.msgbox = QtWidgets.QMessageBox()
            self.msgbox.setIcon(QtWidgets.QMessageBox.Warning)
            self.msgbox.setWindowTitle("Save Record Error")
            self.msgbox.setText(str(err))
            self.msgbox.setStandardButtons(self.msgbox.Ok)
            self.msgbox.show()
            return

        if self.edit_mode:
            self.db.update_record(record)
        else:
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