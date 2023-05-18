import discord
import MainGame.Table
import MainGame.mySQLTables as mySQLTables
import json
from MainGame.RoleGiver import RoleGiver
class Player():
    
    def __init__(self, memberOrID):
        self.alreadyVoted = False
        if type(memberOrID) == discord.member.Member:
            self.user = memberOrID
            self.id = memberOrID.id
        else:
            self.id = memberOrID

        self.inDB = False
        queryRes = mySQLTables.playersTable.selectFromTableWhere("*", "playerID", self.id)
        if queryRes != []:
            self.inDB = True
            self.role = queryRes[0][1]
            self.voteCount = queryRes[0][2]
        else:
            self.role = None
            self.voteCount = 0

    def isMafia(self):
        return self.role == "Mafia"
    
    def isInnocent(self):
        return self.role == "Innocent"

    def getRandomRole(self, roleGiver :RoleGiver):
        self.role = roleGiver.giveRandomRole()
    
    # Bug: player in two different games
    async def notifyPlayerOfRole(self):
        await self.user.create_dm()
        await self.user.dm_channel.send(f"Your role is: {self.role}")

    def incrementVoteCount(self):
        self.voteCount += 1
        print(f"{self.id} was voted")
        
    def removeDataFromDB(self): #TODO
        """
        Remove own data from DB
        """
        mySQLTables.playersTable.deleteFromTableWhere("playerID", self.id)
        self.inDB = False

    def saveInfo(self):
        print("save player information: " + str(self.id))
        # TODO - Try read info from table; if null, then insert; else, update
        if self.inDB:
            mySQLTables.playersTable.updateTableWhere("voteCount", self.voteCount, "playerID", self.id)
            mySQLTables.playersTable.updateTableWhere("hasVoted", self.alreadyVoted, "playerID", self.id)
        else:
            mySQLTables.playersTable.insertIntoTable(self.id, self.role, self.voteCount, self.alreadyVoted)
    
    def setAlreadyVoted(self):
        self.alreadyVoted = True

    def resetAlreadyVoted(self):
        self.alreadyVoted = False
