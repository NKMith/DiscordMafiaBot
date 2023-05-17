from MainGame.Player import Player
from MainGame.RoleGiver import RoleGiver
from MainGame.MyChannel import MyChannel
import discord
import MainGame.Table
import MainGame.mySQLTables as mySQLTables
import json
import env

class MafiaGame():
    def __init__(self, textChannel :discord.TextChannel):
        """ 
        Take in a discord.TextChannel and create a MafiaGame object
        """
        self.discordTextChannel = textChannel # Must be set before calling create_players_list/SetUpPlayersList
        self.setUpMyChannel()
        self.setUpPlayersList()

    def setUpMyChannel(self):
        self.myChannel = MyChannel(self.discordTextChannel)


    def setUpPlayersList(self):
        """PRE: self.myChannel has playersIDArray set up"""
        self.playersList = []
        playerIDList = self.myChannel.playersIDArray
        for id in playerIDList:
            self.playersList.append(Player(id))

    
    def isInitialRound(self):
        return self.myChannel.phase == 1

    
    async def createMafiaChannel(self):
        """ 
        Create a secret channel only for mafias
        """
        guild = self.discordTextChannel.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True) # TODO - Delete this
        }

        # give access to channel to each mafia
        for playerObj in self.playersList:
            if playerObj.role == "Mafia" or playerObj.id == env.GOD_ID: # TODO - Delete GOD_ID
                overwrites[playerObj] = discord.PermissionOverwrite(read_messages=True)

        mafiaChannel = await guild.create_text_channel("MafiaRoom", overwrites=overwrites)
        await mafiaChannel.send(f"Welcome to the game, Mafias. This is the secret channel for mafias of the mafia game in server {guild.name}")
        self.myChannel.setMafiaChannel(mafiaChannel)


    async def killPlayerWithMostVotesAndAnnounce(self): #TODO - players have same votes
        """
        PRE: playersList and MyChannel are set up
        Find and kill the player with most votes
        """
        playerToKill = self.playersList[0]
        for player in self.playersList:
            if player.vote <= playerToKill.vote:
                playerToKill = player

        self.playersList.remove(playerToKill)
        playerToKill.removeDataFromDB()
        
        
        await self.killPlayer(playerToKill)
        

    async def killPlayer(self, playerToKill :Player):
        userToMute = discord.utils.get(self.discordTextChannel.members, id=playerToKill.id)
        self.muteMemberInChannel(userToMute, self.discordTextChannel)
        if playerToKill.isMafia():
            self.muteMemberInChannel(userToMute, self.myChannel.mafiaChannel)
        await self.discordTextChannel.send(f"{userToMute.display_name} has been killed!")
        

    async def muteMemberInChannel(self, userToMute :discord.member.Member, channelToMute):
        """
        Prevent member from being able to chat in the channel
        """
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        await channelToMute.set_permissions(userToMute, overwrite=overwrite)


    def prepForNextRound(self):
        """Increment phase and reset votes"""
        self.myChannel.incrementPhase()
        self.resetVotes()
        
    def resetVotes(self):
        for player in self.playersList:
            player.vote = 0

    def save(self):
        self.saveAllPlayers()
        self.myChannel.saveInfo()
    
    def saveAllPlayers(self):
        for player in self.playersList:
            player.saveInfo()
        print("Saved every player")

    def printAllPlayers(self):
        for player in self.playersList:
            print(player.id)
