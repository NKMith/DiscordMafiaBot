import discord
import MainGame.Table
import MainGame.mySQLTables as mySQLTables
import json
from MainGame.RoleGiver import RoleGiver
class Player():
    
    def __init__(self, memberOrID):
        
        if type(memberOrID) == discord.member.Member:
            self.user = memberOrID
            self.id = memberOrID.id
        else:
            self.id = memberOrID

        self.inDB = False
        self.alreadyVoted = False
        self.isKilled = False
        queryRes = mySQLTables.playersTable.selectFromTableWhere("*", "playerID", self.id)
        if queryRes != []:
            self.inDB = True
            self.role = queryRes[0][1]
            self.voteCount = queryRes[0][2]
            self.alreadyVoted = queryRes[0][3]
            self.isKilled = queryRes[0][4]
        else:
            self.role = None
            self.voteCount = 0

    def isMafia(self):
        return self.role == "Mafia"
    
    def isInnocent(self):
        return self.role == "Innocent"

    def getRandomRole(self, roleGiver :RoleGiver):
        self.role = roleGiver.giveRandomRole()

    def beKilled(self):
        self.isKilled = True

    def isAlive(self):
        return not self.isKilled
    
    def hasAlreadyVoted(self):
        return self.alreadyVoted
    
    async def notifyPlayerOfRole(self):
        await self.user.create_dm()
        print(f"SENDING MESSAGE TO {self.user.display_name}")
        await self.user.dm_channel.send(f"Your role is: {self.role}")

    def incrementVoteCount(self):
        self.voteCount += 1
        print(f"{self.id} was voted; new vote count is {self.voteCount}")
        
    def removeDataFromDB(self):
        """
        Remove own data from DB
        """
        mySQLTables.playersTable.deleteFromTableWhere("playerID", self.id)
        self.inDB = False

    def saveInfo(self):
        print("save player information: " + str(self.id))
        if self.inDB:
            print("PLAYER: UPDATING TABLE")
            mySQLTables.playersTable.updateTableWhere("voteCount", self.voteCount, "playerID", self.id)
            mySQLTables.playersTable.updateTableWhere("hasVoted", self.alreadyVoted, "playerID", self.id)
            mySQLTables.playersTable.updateTableWhere("isKilled", self.isKilled, "playerID", self.id)
        else:
            mySQLTables.playersTable.insertIntoTable(self.id, self.role, self.voteCount, self.alreadyVoted, self.isKilled)
    
    def setAlreadyVoted(self):
        self.alreadyVoted = True

    def resetAlreadyVoted(self):
        self.alreadyVoted = False
