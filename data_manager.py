from dbfread import DBF


class DataManager():
    def __init__(self, db_name):
        self.table = DBF(db_name, load=True)
        self.makeTitleIndex()
        self.currentID = 0

    def getCurrentRecord(self):
        return self.table.records[self.currentID]

    def previousRecord(self):
        if self.currentID != 0:
            self.currentID -= 1

    def nextRecord(self):
        if self.currentID != len(self.table.records) - 1:
            self.currentID += 1

    def makeTitleIndex(self):
        self.titleIndex = []
        recordID = 0
        for record in self.table.records:
            titleRecord = {}
            for column in list(record.keys()):
                titleRecord[column] = record[column]
            titleRecord['RecordID'] = recordID
            titleRecord["TitleSort"] = titleRecord["TITLE"].lower()
            self.titleIndex.append(titleRecord)
            recordID += 1

        self.titleIndex = sorted(self.titleIndex, key=lambda item : item["TitleSort"])