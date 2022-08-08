from dbfread import DBF
import sqlite3

class DataManager():
    def __init__(self, db_name):
        self.table = DBF(db_name, load=True)
        self.currentID = 0
        self.validIndexes = ["RecordID", "Title"]
        self.currentIndex = "RecordID"

    def getCurrentRecord(self):
        return self.table.records[self.currentID]

    def previousRecord(self):
        if self.currentID != 0:
            self.currentID -= 1

    def nextRecord(self):
        if self.currentID != len(self.table.records) - 1:
            self.currentID += 1

    def changeIndex(self, index):
        if index == self.currentIndex:
            return
        if index not in self.validIndexes:
            return

    def makeTitleIndex(self):
        self.titleIndex = []
        recordID = 0
        for record in self.table.records:
            titleRecord = {}
            titleRecord['RecordID'] = recordID
            titleRecord["TitleSort"] = titleRecord["TITLE"].lower()
            self.titleIndex.append(titleRecord)
            recordID += 1

        self.titleIndex = sorted(self.titleIndex, key=lambda item : item["TitleSort"])

    def convertDB(self):
        con = sqlite3.connect("bookinv.db")
        cur = con.cursor()
        cur.execute('''CREATE TABLE books (RecordID INTEGER PRIMARY KEY, Title TEXT, AuthorLast TEXT, Pub TEXT, AcquisDate TEXT, ISBN TEXT, Subj TEXT, Price REAL, LstSaleDate TEXT, MxNumber INTEGER, NumberSold INTEGER, NumOnOrder INTEGER, BoNumber INTEGER, BackOrder INTEGER, PoNum TEXT, SalesHist TEXT, OrderActiv TEXT, PrevPoNum TEXT, OurPrice REAL, OrderInfo TEXT, Discount REAL, ISBN13 TEXT, PW INTEGER, IPS INTEGER, IngO INTEGER, IngT INTEGER, DoDelete INTEGER)''')
        cur.execute("CREATE INDEX idx_author ON books(AuthorLast)")
        cur.execute("CREATE INDEX idx_title ON books(Title)")
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