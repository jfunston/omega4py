from dbfread import DBF
import sqlite3
from bisect import bisect_left

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
        return None

class DataManager():
    def __init__(self, db_name):
        #self.table = DBF(db_name, load=True)
        self.db = sqlite3.connect(db_name)
        cur = self.db.cursor()
        self.records = []
        for record in cur.execute("SELECT * FROM books").fetchall():
            self.records.append(Record(record))
        cur.close()
        self.currentID = 0
        self.validIndexes = ["RecordID", "TITLE"]
        self.currentIndex = "RecordID"

    def getCurrentRecord(self):
        return self.records[self.currentID]

    def previousRecord(self):
        if self.currentID != 0:
            self.currentID -= 1

    def nextRecord(self):
        if self.currentID != len(self.records) - 1:
            self.currentID += 1

    def changeIndex(self, index):
        if index == self.currentIndex:
            return
        if index not in self.validIndexes:
            return
        self.currentIndex = index
        lookupValue = self.getCurrentRecord()[index]
        recordID = self.getCurrentRecord()["RecordID"]

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
        while self.getCurrentRecord()["RecordID"] != recordID:
            self.currentID += 1

    def search(self, searchKey):
        self.currentID = bisect_left(self.records, searchKey.lower(), key= lambda x: x["TITLE"].lower())

    def convertDB(self):
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