import mysql.connector
import env
DB_NAME = "MafiaGame"   # Change this for a suiting DB name for different projects


db = mysql.connector.connect(
    host=env.HOST,
    user=env.USER, #can be any user created
    passwd=env.PASSWORD,
    database=DB_NAME
)
mycursor = db.cursor()

def resetDB():
    mycursor.execute(f"DROP DATABASE {DB_NAME}")
    db.commit()
    mycursor.execute(f"CREATE DATABASE {DB_NAME}")
    db.commit()
    mycursor.execute(f"USE {DB_NAME}") #Need to respecify because database was erased and recreated
    db.commit()




def createTupleStr(iterable): # TODO - utils
    str = f"("
    for i in range(len(iterable)):
        if i == 0:
            str += f"{iterable[i]}"
        else:
            str += f", {iterable[i]}"
    str += ")"
    return str


class Table():
    def __init__(self, name):
        self.name = name
        self.fieldsNames = []
        self.fieldsSetup = []
        
    def addField(self, fieldName :str, fieldSetup :str):
        self.fieldsNames.append(fieldName)
        self.fieldsSetup.append(fieldSetup)
    
    def getTableName(self):
        return self.name

    def getFieldSetupStr(self, index):
        return f"{self.fieldsNames[index]} {self.fieldsSetup[index]}"

    def getCreateTableCommand(self):
        str = f"CREATE TABLE {self.name} ("
        for i in range(len(self.fieldsNames)):
            if i == 0:
                str += self.getFieldSetupStr(i)
            else:
                str += f", {self.getFieldSetupStr(i)}"
        str += ")"
        return str
    
    def getInsertIntoCommand(self):
        str = f"INSERT INTO {self.name} {createTupleStr(self.fieldsNames)} VALUES "
        tmp = []
        for i in self.fieldsNames:
            tmp.append(f"%s")
        str += createTupleStr(tmp)
        return str
    
    def getSelectFromCommand(self, selectField):
        str = f"SELECT {selectField} FROM {self.name}"
        return str

    def getSelectFromTableWhereCommand(self, selectField, criteriaField, criteriaValue):
        str = self.getSelectFromCommand(selectField)
        str += f" WHERE {criteriaField} = {criteriaValue}"
        return str
    
    def createTable(self):
        print(self.getCreateTableCommand())
        mycursor.execute(self.getCreateTableCommand())
        db.commit()

    
    def insertIntoTable(self, *fieldsVals):
        mycursor.execute(self.getInsertIntoCommand(), fieldsVals)
        db.commit()

    def selectAllFromTable(self):
        print(self.getSelectFromCommand("*"))
        mycursor.execute(self.getSelectFromCommand("*"))
        db.commit()

    

    def selectFromTableWhere(self, selectField, criteriaField, criteriaValue):
        """ 
        Returns a list of query results that matches criteriaValue
        """
        mycursor.execute(self.getSelectFromTableWhereCommand(selectField, criteriaField, criteriaValue))
        return mycursor.fetchall()
        #mycursor.fetchall() returns a list of all rows (returns a list of tuples)
        #fetchone()
    
    def printAllFromTable(self):
        self.selectAllFromTable()
        for x in mycursor:
            print(x)

    def updateTableWhere(self, updateField, newValue, criteriaField, criteriaValue):
        mycursor.execute(f"UPDATE {self.name} SET {updateField} = {newValue} WHERE {criteriaField} = {criteriaValue}")
        db.commit()

    def deleteFromTableWhere(self, criteriaField, criteriaValue):
        mycursor.execute(f"DELETE FROM {self.name} WHERE {criteriaField} = {criteriaValue}")
        db.commit()





# Channels
# tableName = channel
# Columns
#   ID: bigint
#   PlayersArray: []

""" channelTableInfo = Table("ActiveChannels")
print("OK")
channelTableInfo.addField("channelID", "bigint unsigned PRIMARY KEY NOT NULL")
channelTableInfo.addField("playersArray", "JSON")
print(channelTableInfo.getCreateTableCommand())
#mycursor.execute("CREATE TABLE Person (name VARCHAR(50), age smallint UNSIGNED, personID int PRIMARY KEY AUTO_INCREMENT)") 
print(channelTableInfo.getInsertIntoCommand())
print(channelTableInfo.getSelectFromTableWhereCommand("*", "age", "12304")) """