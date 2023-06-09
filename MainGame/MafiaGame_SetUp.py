""" 
A child of main Mafia Game object for setting up a new game

"""

from MainGame.Player import Player
from MainGame.RoleGiver import RoleGiver
from MainGame.MafiaGameMain import MafiaGame
import discord
import MainGame.mySQLTables as mySQLTables
import MainGame.Validator as Validator

class MafiaGame_SetUp(MafiaGame):
    def __init__(self, textChannel :discord.TextChannel, players_displayNames :tuple):
        self.players_displayNames = players_displayNames

        super().__init__(textChannel)
        self.myChannel.setPlayersIDArray(self.createIDArr(self.playersList))
        self.roleGiver = RoleGiver(len(self.playersList))

        self.unaddedMembersDisplayNames = []

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

        if self.players_displayNames == ():
            for member in self.discordTextChannel.members:
                self.addMemberToPlayersListAsPlayer(member)
        else:
            for displayName in self.players_displayNames:
                member = discord.utils.get(self.discordTextChannel.members, display_name=displayName)
                self.addMemberToPlayersListAsPlayer(member)


    
    def addMemberToPlayersListAsPlayer(self, member :discord.Member):
        """ Will not announce which players weren't added because of async (call separate func manually) """
        if member == None:
            return

        if Validator.isPlayerOrMemberInDB(member):
            self.unaddedMembersDisplayNames.append(member.display_name)
            return

        if not member.bot:
            newPlayer = Player(member)
            self.playersList.append(newPlayer)

    async def announceWhichPlayersWerentAdded(self):
        if self.unaddedMembersDisplayNames == []:
            return
        announceStr = ""
        for displayName in self.unaddedMembersDisplayNames:
            announceStr += f"{displayName}\n"
        await self.discordTextChannel.send(f"These people weren't added because they already are in a game: \n{announceStr}")
        
    

    def giveAllPlayerRoles(self):
        for player in self.playersList:
            player.getRandomRole(self.roleGiver)
        print("Gave every player a role")

    async def notifyAllPlayersAboutRole(self):
        for player in self.playersList:
            await player.notifyPlayerOfRole()
