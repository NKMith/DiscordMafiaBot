
from MainGame.Player import Player
from MainGame.RoleGiver import RoleGiver
from MainGame.MyChannel import MyChannel
import discord
import json
import MainGame.mySQLTables as mySQLTables


class MafiaGame_SetUp:
    def __init__(self, initialChannel :discord.TextChannel, players_displayNames :tuple):
        self.players_displayNames = players_displayNames
        self.playersList = self.createPlayersList(initialChannel)
        self.myChannel = MyChannel(initialChannel)
        self.myChannel.setPlayersIDArray(self.createIDArr(self.playersList))
        self.roleGiver = RoleGiver(len(self.playersList))
        print("MafiaGame instantiated")

    def createIDArr(self, iterable): #iterable elements must have field id
        retArr = []
        for x in iterable:
            retArr.append(x.id)
        return retArr


    def createPlayersList(self, initialChannel) -> list:
        playersArr = []
        # if not specifically mentioned, add all the non-bot members
        if self.players_displayNames == ():
            for member in initialChannel.members:
                if not member.bot:
                    print(type(member))
                    newPlayer = Player(member)
                    playersArr.append(newPlayer)
        else:
            for displayName in self.players_displayNames:
                member = discord.utils.get(initialChannel.members, display_name=displayName)
                if member != None and not member.bot:
                    newPlayer = Player(member)
                    playersArr.append(newPlayer)

        print("Created playersArr")
        return playersArr

    def giveAllPlayerRoles(self):
        for player in self.playersList:
            self.roleGiver.printInfo()
            player.getRandomRole(self.roleGiver)
        print("Gave every player a role")

    def save(self):
        """Save all players and save channel"""
        self.saveAllPlayers()
        self.myChannel.saveInfo()

    def saveAllPlayers(self):
        for player in self.playersList:
            player.saveInfo()
        print("Saved every player")

    def printAllPlayers(self):
        for player in self.playersList:
            print(player.id)

    async def notifyAllPlayersAboutRole(self):
        for player in self.playersList:
            await player.notifyPlayerOfRole()
