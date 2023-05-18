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
        return self.myChannel.phase == 0
    
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


    def votePlayerIfValid(self, voterUser :discord.member.Member, voteeDisplayName):
        voteeUser :discord.member.Member = discord.utils.get(self.discordTextChannel, display_name=voteeDisplayName)
        voterPlayer = self.getPlayerWithID(voterUser.id)
        voteePlayer = self.getPlayerWithID(voteeUser.id)
        #self.votePlayerWithID(voterUser.id, voteeUser.id)

        if voterPlayer.alreadyVoted():
            self.discordTextChannel.send(f"{voterUser.display_name}, you already voted!")
            return

        if self.myChannel.isMafiaPhase() and voterPlayer.isInnocent(): #TODO - Mafia tries to vote in Mafia phase but in the general channel
            self.discordTextChannel.send("You aren't allowed to vote during this phase!")
        else:
            voterPlayer.setAlreadyVoted()
            voteePlayer.incrementVoteCount()

    def getPlayerWithID(self, id :int) -> Player:
        for player in self.playersList:   
            if player.id == id:
                return player

    
    def votePlayerWithID(self, voterID, voteeID): #TODO - Unused
        """Find players using IDs, set voter's voteBool true and increment votee's vote count"""
        votee :Player = None
        voter :Player = None
        for player in self.playersList:
            if player.id == voterID:
                voter == player
            elif player.id == voteeID:
                votee == player

        voter.setAlreadyVoted()
        votee.incrementVoteCount()

    async def announcePlayerVoteCounts(self):
        await self.discordTextChannel.send(f"This are the votes each player got in Phase {self.myChannel.phase}:")
        for player in self.playersList:
            await self.discordTextChannel.send(f"This are the votes each player got in Phase {self.myChannel.phase}:")
            


    async def killPlayerWithMostVotesAndAnnounce(self): #TODO - players have same votes
        """
        PRE: playersList and MyChannel are set up
        Find and kill the player with most votes
        """
        playerToKill :Player = self.playersList[0]
        for player in self.playersList:
            if player.voteCount <= playerToKill.voteCount:
                playerToKill = player

        self.playersList.remove(playerToKill)
        playerToKill.removeDataFromDB()
        await self.killPlayerAndAnnounce(playerToKill)
        

    async def killPlayerAndAnnounce(self, playerToKill :Player):
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
        self.resetAllVotes()
        
    def resetAllVotes(self):
        """Make everyone's voteCount 0 and reset their hasVoted boolean"""
        for player in self.playersList:
            player.voteCount = 0
            player.resetVoted()

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
