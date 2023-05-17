import discord
import MainGame.Table as Table
import MainGame.mySQLTables as mySQLTables
import json

# Odd phases are Mafia-Kill phases
# Even pharases are Citizen-Vote Phases
class MyChannel:
    def __init__(self, channelOrID):
        self.mafiaChannel = None
        self.mafiaChannelID = None
        if type(channelOrID) == discord.TextChannel:
            self.id = channelOrID.id
        else:
            self.id = channelOrID
        
        self.inDB = False
        queryRes = mySQLTables.channelTable.selectFromTableWhere("*", "channelID", self.id)
        if queryRes != []:
            self.inDB = True
            self.playersIDArray = json.loads(queryRes[0][1])
            self.phase = queryRes[0][2]
        else:
            self.playersIDArray = []
            self.phase = 0

    def setPlayersIDArray(self, playersIDArray):
        self.playersIDArray = playersIDArray
    
    def setMafiaChannel(self, mafiaChannel :discord.TextChannel):
        self.mafiaChannel = mafiaChannel
        self.mafiaChannelID = self.mafiaChannel.id

    def saveInfo(self):
        # Channel ID | PlayersArray: []; array of IDs of players | phase
        if self.inDB:
            if self.mafiaChannel == None:
                mySQLTables.channelTable.updateTableWhere("phase", self.phase, "channelID", self.id)
            else:
                mySQLTables.channelTable.updateTableWhere("phase", self.phase, "channelID", self.id)
                mySQLTables.channelTable.updateTableWhere("mafiaChannelID", self.mafiaChannel.id, "channelID", self.id)
        else:
            if self.mafiaChannel == None:
                mySQLTables.channelTable.insertIntoTable(self.id, json.dumps(self.playersIDArray), self.phase, "NULL")
            else:
                mySQLTables.channelTable.insertIntoTable(self.id, json.dumps(self.playersIDArray), self.phase, self.mafiaChannelID)

    def incrementPhase(self):
        self.phase += 1
        #mySQLTables.channelTable.updateTableWhere("phase", self.phase, "channelID", self.id)
