from dbfread import DBF
import sqlite3
from bisect import bisect_left
from datetime import date


class Record():
    def __init__(self, data):
        self.data = data

    def __getitem__(self, item):
        if item == "TITLE":
            return self.data[1]
        elif item == "AUTHORLAST":
            return self.data[2]
        elif item == "RecordID":
            return self.data[0]
        elif item == "Subj":
            return self.data[6]
        elif item == "Price":
            return self.data[7]
        elif item == "LstSaleDate":
            return self.data[8]
        elif item == "MxNumber":
            return self.data[9]
        elif item == "NumberSold":
            return self.data[10]
        elif item == "SalesHist":
            return self.data[15]
        elif item == "OrderActiv":
            return self.data[16]
        return None


class DataManager():
    def __init__(self, db_name):
        #self.table = DBF(r"F:\alpha4v8\BookInv\BOOKINV.DBF", load=True)
        #self.convert_db()
        self.db = sqlite3.connect(db_name)
        cur = self.db.cursor()
        self.records = []
        for record in cur.execute("SELECT * FROM books").fetchall():
            self.records.append(Record(record))
        cur.close()
        self.currentID = 0
        self.validIndexes = ["RecordID", "TITLE"]
        self.currentIndex = "RecordID"
        self.totalRecords = len(self.records)

    def get_total_records(self):
        return self.totalRecords

    def get_current_id(self):
        return self.currentID

    def set_current_id(self, id):
        self.currentID = id

    def get_current_record(self):
        return self.records[self.currentID]

    def previous_record(self):
        if self.currentID != 0:
            self.currentID -= 1

    def next_record(self):
        if self.currentID != len(self.records) - 1:
            self.currentID += 1

    def make_sale(self):
        today = date.today().strftime("%d/%m/%Y")
        cur = self.db.cursor()
        update = "UPDATE books SET LstSaleDate = ?, SalesHist = ?, NumberSold = ?, OrderActiv = ? WHERE RecordID = ?"
        hist = self.get_current_record()["SalesHist"] + " " + today + ","
        sold = 0
        if self.get_current_record()["NumberSold"] is None:
            sold = 1
        else:
            sold = self.get_current_record()["NumberSold"] + 1
        cur.execute(update, (today, hist, str(sold), "200", str(self.get_current_record()["RecordID"])))
        self.db.commit()
        cur.execute("SELECT * FROM books WHERE RecordID = ?", (str(self.get_current_record()["RecordID"]),))
        data = cur.fetchone()
        self.records[self.currentID] = Record(data)

    def change_index(self, index):
        if index == self.currentIndex:
            return
        if index not in self.validIndexes:
            return
        self.currentIndex = index
        lookupValue = self.get_current_record()[index]
        recordID = self.get_current_record()["RecordID"]

        cur = self.db.cursor()
        self.records = []
        order_by = ""
        if index != "RecordID":
            order_by = " ORDER BY " + index + " COLLATE NOCASE"
        for record in cur.execute("SELECT * FROM books" + order_by).fetchall():
            self.records.append(Record(record))

        if index == "RecordID":
            self.currentID = recordID - 1
            return

        self.currentID = bisect_left(self.records, lookupValue.lower(), key= lambda x: x[index].lower())
        while self.get_current_record()["RecordID"] != recordID:
            self.currentID += 1

    def search(self, searchKey):
        self.currentID = bisect_left(self.records, searchKey.lower(), key= lambda x: x["TITLE"].lower())

    def substring_search(self, searchKey):
        like = "%" + searchKey + "%"
        self.currentID = 0
        self.currentIndex = "Search"

        cur = self.db.cursor()
        self.records = []
        order_by = " ORDER BY Title COLLATE NOCASE"
        for record in cur.execute("SELECT * FROM books WHERE Title LIKE ?" + order_by, (like,)).fetchall():
            self.records.append(Record(record))

    def convert_db(self):
        con = sqlite3.connect("bookinv.db")
        cur = con.cursor()
        cur.execute('''CREATE TABLE books (RecordID INTEGER PRIMARY KEY, Title TEXT, AuthorLast TEXT, Pub TEXT, AcquisDate TEXT, ISBN TEXT, Subj TEXT, Price REAL, LstSaleDate TEXT, MxNumber INTEGER, NumberSold INTEGER, NumOnOrder INTEGER, BoNumber INTEGER, BackOrder INTEGER, PoNum TEXT, SalesHist TEXT, OrderActiv TEXT, PrevPoNum TEXT, OurPrice REAL, OrderInfo TEXT, Discount REAL, ISBN13 TEXT, PW INTEGER, IPS INTEGER, IngO INTEGER, IngT INTEGER, DoDelete INTEGER)''')
        cur.execute("CREATE INDEX idx_author ON books(AuthorLast COLLATE NOCASE)")
        cur.execute("CREATE INDEX idx_title ON books(Title COLLATE NOCASE)")
        idx = 1
        for record in self.table.records:
            insertSQL = "INSERT INTO books VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
                        (idx, record["TITLE"], record["AUTHORLAST"], record["PUB"], record["ACQUISDATE"], record["ISBN"], record["SUBJ"], \
                         record["PRICE"], record["LSTSALEDAT"], record["MXNUMBER"], record["NUMBERSOLD"], record["NUMONORDER"], record["BONUMBER"], \
                         record["BACKORDER"], record["PONUM"], record["SALES_HIST"], record["ORDERACTIV"], record["PREVPONUM"], record["OURPRICE"], \
                         record["ORDERINFO"], record["DISCOUNT"], record["ISBN13"], record["PW"], record["IPS"], record["INGO"], \
                         record["INGT"], record["DELETE"])
            print(insertSQL)
            cur.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (idx, record["TITLE"], record["AUTHORLAST"], record["PUB"], record["ACQUISDATE"], record["ISBN"],
                        record["SUBJ"], \
                        record["PRICE"], record["LSTSALEDAT"], record["MXNUMBER"], record["NUMBERSOLD"],
                        record["NUMONORDER"], record["BONUMBER"], \
                        record["BACKORDER"], record["PONUM"], record["SALES_HIST"], record["ORDERACTIV"],
                        record["PREVPONUM"], record["OURPRICE"], \
                        record["ORDERINFO"], record["DISCOUNT"], record["ISBN13"], record["PW"], record["IPS"],
                        record["INGO"], \
                        record["INGT"], record["DELETE"]))
            idx += 1
        con.commit()
        con.close()