
from MainGame.Player import Player
from MainGame.RoleGiver import RoleGiver
from MainGame.MyChannel import MyChannel
from MainGame.MafiaGameMain import MafiaGame
import discord
import json
import MainGame.mySQLTables as mySQLTables


class MafiaGame_SetUp(MafiaGame):
    def __init__(self, textChannel :discord.TextChannel, players_displayNames :tuple):
        self.players_displayNames = players_displayNames
        super().__init__(textChannel)
        #self.setUpPlayersList(textChannel)
        self.myChannel.setPlayersIDArray(self.createIDArr(self.playersList))
        self.roleGiver = RoleGiver(len(self.playersList))

    def createIDArr(self, iterable): #iterable elements must have field id
        retArr = []
        for x in iterable:
            retArr.append(x.id)
        return retArr

    def setUpPlayersList(self):
        """
        Overriding: assumes self.myChannel doesn't have playersIDArray set up
        Instead uses displayNames tuple to set up players list
        """
        self.playersList = []
        # if not specifically mentioned, add all the non-bot members
        # TODO - handle cases where there are different users with duplicate names
        if self.players_displayNames == ():
            for member in self.discordTextChannel.members:
                if not member.bot:
                    newPlayer = Player(member)
                    self.playersList.append(newPlayer)
        else:
            for displayName in self.players_displayNames:
                member = discord.utils.get(self.discordTextChannel.members, display_name=displayName)
                if member != None and not member.bot:
                    newPlayer = Player(member)
                    self.playersList.append(newPlayer)

    def giveAllPlayerRoles(self):
        for player in self.playersList:
            self.roleGiver.printInfo()
            player.getRandomRole(self.roleGiver)
        print("Gave every player a role")

    async def notifyAllPlayersAboutRole(self):
        for player in self.playersList:
            await player.notifyPlayerOfRole()
