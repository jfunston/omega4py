import sqlite3
from bisect import bisect_left
from datetime import date


class Record():
    def __init__(self, data):
        self.data = data

    def __getitem__(self, item):
        if item == "RecordID":
            return self.data[0]
        elif item == "Title":
            return self.data[1]
        elif item == "AuthorLast":
            return self.data[2]
        elif item == "Pub":
            return self.data[3]
        elif item == "AcquisDate":
            return self.data[4]
        elif item == "ISBN":
            return self.data[5]
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
        elif item == "NumOnOrder":
            return self.data[11]
        elif item == "BoNumber":
            return self.data[12]
        elif item == "BackOrder":
            return self.data[13]
        elif item == "PoNum":
            return self.data[14]
        elif item == "SalesHist":
            return self.data[15]
        elif item == "OrderActiv":
            return self.data[16]
        elif item == "PrevPoNum":
            return self.data[17]
        #elif item == "OurPrice":
        #    return self.data[18]
        elif item == "OrderInfo":
            return self.data[19]
        #elif item == "Discount":
        #    return self.data[20]
        #elif item == "ISBN13":
        #    return self.data[21]
        elif item == "PW":
            return self.data[22]
        elif item == "IPS":
            return self.data[23]
        elif item == "IngO":
            return self.data[24]
        elif item == "IngT":
            return self.data[25]
        return None


def regularize_user_record(record):
    text_fields = ["Title", "AuthorLast", "Pub", "AcquisDate", "ISBN", "Subj", "LstSaleDate", "PoNum", "SalesHist", "OrderActiv", "PrevPoNum", "OrderInfo", "ISBN13"]
    int_fields = ["MxNumber", "NumberSold", "NumOnOrder", "BoNumber", "BackOrder", "PW", "IPS", "IngO", "IngT", "DoDelete"]
    float_fields = ["Price", "OurPrice", "Discount"]
    for text_field in text_fields:
        if text_field not in record.keys():
            record[text_field] = None
    for int_field in int_fields:
        if int_field not in record.keys():
            record[int_field] = None
    for float_field in float_fields:
        if float_field not in record.keys():
            record[float_field] = None
    return record


class DataManager():
    def __init__(self, db_name):
        #self.table = DBF(r"F:\alpha4v8\BookInv\BOOKINV.DBF", load=True)
        #self.convert_db()
        try:
            self.db = sqlite3.connect(db_name)
            cur = self.db.cursor()
            self.records = []
            for record in cur.execute("SELECT * FROM books").fetchall():
                self.records.append(Record(record))
            cur.close()
            self.currentID = 0
            self.validIndexes = ["RecordID", "Title", "AuthorLast", "Subj+Title", "Pub+Title", "OrderActiv", "ISBN"]
            self.currentIndex = "RecordID"
            self.totalRecords = len(self.records)
        except:
            self.totalRecords = 0
            self.record = []

    def get_total_records(self):
        return self.totalRecords

    def get_current_id(self):
        return self.currentID

    def set_current_id(self, id):
        self.currentID = id

    def get_max_record_id(self):
        query = "SELECT MAX(RecordId) FROM books"
        cur = self.db.cursor()
        cur.execute(query)
        data = cur.fetchone()
        cur.close()
        return data[0]

    def get_current_record(self):
        return self.records[self.currentID]

    def previous_record(self):
        if self.currentID != 0:
            self.currentID -= 1

    def next_record(self):
        if self.currentID != len(self.records) - 1:
            self.currentID += 1

    def refresh_cur_record(self):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM books WHERE RecordID = ?", (str(self.get_current_record()["RecordID"]),))
        data = cur.fetchone()
        self.records[self.currentID] = Record(data)

    def make_sale(self):
        today = date.today().strftime("%m/%d/%Y")
        cur = self.db.cursor()
        update = "UPDATE books SET LstSaleDate = ?, SalesHist = ?, NumberSold = ?, OrderActiv = ? WHERE RecordID = ?"
        hist = ""
        # TODO error handling and fallback
        if self.get_current_record()["SalesHist"].find(today) == -1:
            hist = today +", " + self.get_current_record()["SalesHist"]
        elif self.get_current_record()["SalesHist"].find(today + " (") == -1:
            split = self.get_current_record()["SalesHist"].split(',', 1)
            hist = today + " (2)," + split[1]
        else:
            split = self.get_current_record()["SalesHist"].split('(', 1)
            num_split = split[1].split(')', 1)
            count = int(num_split[0])
            count += 1
            split = self.get_current_record()["SalesHist"].split(',', 1)
            hist = today + " (" + str(count) + ")," + split[1]
        sold = 0
        if self.get_current_record()["NumberSold"] is None:
            sold = 1
        else:
            sold = self.get_current_record()["NumberSold"] + 1
        cur.execute(update, (today, hist, str(sold), "200", str(self.get_current_record()["RecordID"])))
        self.db.commit()
        cur.close()
        self.refresh_cur_record()

    def change_index(self, index):
        if index not in self.validIndexes:
            return
        self.currentIndex = index
        lookupValue = self.get_current_record()[index.split('+')[0]]
        recordID = self.get_current_record()["RecordID"]

        cur = self.db.cursor()
        self.records = []
        order_by = ""
        if index != "RecordID":
            order_by = " ORDER BY "
            index_parts = index.split('+')
            for index_part in index_parts:
                order_by += index_part + " COLLATE NOCASE, "
            order_by = order_by[:-2]
        for record in cur.execute("SELECT * FROM books" + order_by).fetchall():
            self.records.append(Record(record))
        cur.close()

        if index == "RecordID":
            self.currentID = bisect_left(self.records, lookupValue, key= lambda x: x[index.split('+')[0]])
        else:
            self.currentID = bisect_left(self.records, lookupValue.lower(), key= lambda x: x[index.split('+')[0]].lower())
        while self.get_current_record()["RecordID"] != recordID:
            self.currentID += 1

    def search(self, searchKey):
        searchIndex = self.currentIndex
        if "+" in self.currentIndex:
            searchIndex = self.currentIndex.split('+')[0]

        if self.currentIndex != "RecordID":
            searchKey = searchKey.lower()
            self.currentID = bisect_left(self.records, searchKey, key= lambda x: x[searchIndex].lower())
        else:
            self.currentID = bisect_left(self.records, int(searchKey), key= lambda x: x[searchIndex])

    def delete_current_record(self):
        # TODO snapshot
        cur = self.db.cursor()
        cur.execute("DELETE FROM books WHERE RecordID = " + str(self.get_current_record()["RecordID"]))
        self.db.commit()
        cur.close()
        del self.records[self.currentID]
        if self.currentID >= len(self.records):
            self.currentID = len(self.records) - 1
        self.totalRecords -= 1

    def substring_search(self, searchKey):
        like = "%" + searchKey + "%"
        self.currentID = 0
        self.currentIndex = "Search"

        cur = self.db.cursor()
        self.records = []
        order_by = " ORDER BY Title COLLATE NOCASE"
        for record in cur.execute("SELECT * FROM books WHERE Title LIKE ?" + order_by, (like,)).fetchall():
            self.records.append(Record(record))
        cur.close()

    def count_search(self, field, searchKey):
        query = "SELECT COUNT(*) FROM books WHERE " + field + " = ?"
        cur = self.db.cursor()
        result = cur.execute(query, (searchKey,)).fetchall()
        cur.close()
        return result[0][0]

    def find_replace(self, field, searchKey, replace):
        query = f"UPDATE books SET {field} = ? WHERE {field} = ?"
        cur = self.db.cursor()
        cur.execute(query, (replace, searchKey)).fetchall()
        self.db.commit()
        cur.close()
        prvIndex = self.currentIndex
        self.currentIndex = "tmp"
        self.change_index(prvIndex)

    def ordercode_search(self, search):
        where = ""
        if search == "200":
            where = "OrderActiv = 200"
        elif search == "":
            where = 'OrderActiv != ""'
        self.currentID = 0
        self.currentIndex = "Search"

        cur = self.db.cursor()
        self.records = []
        order_by = " ORDER BY Title COLLATE NOCASE"
        for record in cur.execute("SELECT * FROM books WHERE " + where + order_by).fetchall():
            self.records.append(Record(record))
        cur.close()

    def insert_record(self, record):
        record["RecordID"] = self.get_max_record_id() + 1
        record = regularize_user_record(record)

        cur = self.db.cursor()
        cur.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (record["RecordID"], record["Title"], record["AuthorLast"], record["Pub"], record["AcquisDate"], record["ISBN"],
                    record["Subj"], \
                    record["Price"], record["LstSaleDate"], record["MxNumber"], record["NumberSold"],
                    record["NumOnOrder"], record["BoNumber"], \
                    record["BackOrder"], record["PoNum"], record["SalesHist"], record["OrderActiv"],
                    record["PrevPoNum"], record["OurPrice"], \
                    record["OrderInfo"], record["Discount"], record["ISBN13"], record["PW"], record["IPS"],
                    record["IngO"], \
                    record["IngT"], record["DoDelete"]))
        self.db.commit()
        cur.close()

    def update_record(self, record):
        record = regularize_user_record(record)

        cur = self.db.cursor()
        cur.execute("UPDATE books SET Title = ?, AuthorLast = ?, Pub = ?, AcquisDate = ?, ISBN = ?, Subj = ?, Price = ?, LstSaleDate = ?, MxNumber = ?, NumberSold = ?, NumOnOrder = ?, BoNumber = ?, BackOrder = ?, PoNum = ?, SalesHist = ?, OrderActiv = ?, PrevPoNum = ?, OurPrice = ?, OrderInfo = ?, Discount = ?, ISBN13 = ?, PW = ?, IPS = ?, IngO = ?, IngT = ?, DoDelete = ? WHERE RecordID = ?",
                    (record["Title"], record["AuthorLast"], record["Pub"], record["AcquisDate"], record["ISBN"],
                    record["Subj"], \
                    record["Price"], record["LstSaleDate"], record["MxNumber"], record["NumberSold"],
                    record["NumOnOrder"], record["BoNumber"], \
                    record["BackOrder"], record["PoNum"], record["SalesHist"], record["OrderActiv"],
                    record["PrevPoNum"], record["OurPrice"], \
                    record["OrderInfo"], record["Discount"], record["ISBN13"], record["PW"], record["IPS"],
                    record["IngO"], \
                    record["IngT"], record["DoDelete"], record["RecordID"]))
        self.db.commit()
        cur.close()
        self.refresh_cur_record()

    def convert_db(self):
        con = sqlite3.connect("bookinv.db")
        cur = con.cursor()
        cur.execute('''CREATE TABLE books (RecordID INTEGER PRIMARY KEY, Title TEXT, AuthorLast TEXT, Pub TEXT, AcquisDate TEXT, ISBN TEXT, Subj TEXT, Price REAL, LstSaleDate TEXT, MxNumber INTEGER, NumberSold INTEGER, NumOnOrder INTEGER, BoNumber INTEGER, BackOrder INTEGER, PoNum TEXT, SalesHist TEXT, OrderActiv TEXT, PrevPoNum TEXT, OurPrice REAL, OrderInfo TEXT, Discount REAL, ISBN13 TEXT, PW INTEGER, IPS INTEGER, IngO INTEGER, IngT INTEGER, DoDelete INTEGER)''')
        cur.execute("CREATE INDEX idx_author ON books(AuthorLast COLLATE NOCASE)")
        cur.execute("CREATE INDEX idx_title ON books(Title COLLATE NOCASE)")
        cur.execute("CREATE INDEX idx_isbn ON books(ISBN COLLATE NOCASE)")
        cur.execute("CREATE INDEX idx_subj_title ON books(Subj COLLATE NOCASE, Title COLLATE NOCASE)")
        cur.execute("CREATE INDEX idx_pub_title ON books(Pub COLLATE NOCASE, Title COLLATE NOCASE)")
        cur.execute("CREATE INDEX idx_orderactiv ON books(OrderActiv COLLATE NOCASE)")
        idx = 1
        for record in self.table.records:
            acqdate = None
            if record["ACQUISDATE"] is not None:
                acqdate = record["ACQUISDATE"].strftime("%m/%d/%Y")
            lstsale = None
            if record["LSTSALEDAT"] is not None:
                lstsale = record["LSTSALEDAT"].strftime("%m/%d/%Y")
            if record["TITLE"] is None or record["TITLE"] == "":
                continue
            insertSQL = "INSERT INTO books VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
                        (idx, record["TITLE"], record["AUTHORLAST"], record["PUB"], acqdate, record["ISBN"], record["SUBJ"], \
                         record["PRICE"], lstsale, record["MXNUMBER"], record["NUMBERSOLD"], record["NUMONORDER"], record["BONUMBER"], \
                         record["BACKORDER"], record["PONUM"], record["SALES_HIST"], record["ORDERACTIV"], record["PREVPONUM"], record["OURPRICE"], \
                         record["ORDERINFO"], record["DISCOUNT"], record["ISBN13"], record["PW"], record["IPS"], record["INGO"], \
                         record["INGT"], record["DELETE"])
            print(insertSQL)
            res = cur.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (idx, record["TITLE"], record["AUTHORLAST"], record["PUB"], acqdate, record["ISBN"],
                        record["SUBJ"], \
                        record["PRICE"], lstsale, record["MXNUMBER"], record["NUMBERSOLD"],
                        record["NUMONORDER"], record["BONUMBER"], \
                        record["BACKORDER"], record["PONUM"], record["SALES_HIST"], record["ORDERACTIV"],
                        record["PREVPONUM"], record["OURPRICE"], \
                        record["ORDERINFO"], record["DISCOUNT"], record["ISBN13"], record["PW"], record["IPS"],
                        record["INGO"], \
                        record["INGT"], record["DELETE"]))
            if res.lastrowid != idx:
                raise ValueError("Lost insert")
            idx += 1
        con.commit()
        con.close()