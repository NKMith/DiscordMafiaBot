from MainGame.Player import Player
from MainGame.RoleGiver import RoleGiver
from MainGame.MyChannel import MyChannel
import discord
import MainGame.Table
import MainGame.mySQLTables as mySQLTables
import json
import env
import time

#TODO - God class
class MafiaGame():
    def __init__(self, textChannel :discord.TextChannel):
        """ 
        Take in a discord.TextChannel and create a MafiaGame object
        """
        self.discordTextChannel = textChannel
        self.setUpMyChannel()
        self.setUpPlayersList()

    def setUpMyChannel(self):
        self.myChannel = MyChannel(self.discordTextChannel)


    def setUpPlayersList(self):
        """PRE: self.myChannel has playersIDArray set up"""
        self.playersList = []
        playerIDList = self.myChannel.playersIDList
        for id in playerIDList:
            self.playersList.append(Player(id))
        print(self.playersList)

    
    def isInitialRound(self):
        return self.myChannel.phase == 0
    
    async def createMafiaChannel(self):
        """ 
        PRE: every player already got their role
        Create a secret channel only for mafias
        """
        guild = self.discordTextChannel.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True) # TODO - Delete this
        }

        # give access to channel to each mafia
        for playerObj in self.playersList:
            playerObj :Player = playerObj
            if playerObj.isMafia() or playerObj.id == env.GOD_ID: # TODO - Delete GOD_ID
                overwrites[playerObj] = discord.PermissionOverwrite(read_messages=True)

        mafiaChannel = await guild.create_text_channel("MafiaRoom", overwrites=overwrites)
        await mafiaChannel.send(f"Welcome to the game, Mafias. This is the secret channel for mafias of the mafia game in server {guild.name}")
        self.myChannel.setMafiaChannel(mafiaChannel)
        print("Created a Mafia Channel")


    async def votePlayerIfValid(self, voterUser :discord.member.Member, voteeDisplayName):
        voteeUser :discord.member.Member = discord.utils.get(self.discordTextChannel.members, display_name=voteeDisplayName)
        voterPlayer = self.getPlayerWithID(voterUser.id)
        voteePlayer = self.getPlayerWithID(voteeUser.id)

        if voterPlayer.hasAlreadyVoted():
            #print(f"MAFIA CHANNEL NAME: {self.myChannel.mafiaChannel.name}")
            msg = f"{voterUser.display_name}, you already voted!"
            if self.myChannel.isMafiaPhase(): #announcement should go to the Mafia channel if voted from there
                await self.myChannel.mafiaChannel.send(msg)
            else:
                await self.discordTextChannel.send(msg)
            return

        if self.myChannel.isMafiaPhase() and voterPlayer.isInnocent(): 
            await self.discordTextChannel.send("You aren't allowed to vote during this phase!")
            return
        
    
        #TODO - Mafia tries to vote in Mafia phase but in the general channel
        # print(f"already voted: {voterPlayer.hasAlreadyVoted()}")
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
            player :Player = player
            print(f"{player.id}'s vote count is {player.voteCount}")
            if player.voteCount >= playerToKill.voteCount: #TODO - check >=
                playerToKill = player

        print(f"PLAYER TO KILL: {playerToKill.id}")
        await self.killPlayerAndAnnounce(playerToKill)
        

    async def killPlayerAndAnnounce(self, playerToKill :Player):
        userToMute = discord.utils.get(self.discordTextChannel.members, id=playerToKill.id)
        await self.muteMemberInChannel(userToMute, self.discordTextChannel)
        if playerToKill.isMafia():
            await self.muteMemberInChannel(userToMute, self.myChannel.mafiaChannel)
        playerToKill.beKilled()
        await self.discordTextChannel.send(f"{userToMute.display_name} has been killed!")
        

    async def muteMemberInChannel(self, userToMute :discord.member.Member, channelToMute):
        """
        Prevent member from being able to chat in the channel
        """
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        await channelToMute.set_permissions(userToMute, overwrite=overwrite)

    async def unmuteMemberInChannel(self, userToMute :discord.member.Member, channelToMute):
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
            player :Player = player
            player.voteCount = 0
            player.resetAlreadyVoted()

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

    async def finishGame(self):
        await self.announceWinner()
        await self.announceWhoAreTheMafias()
        await self.reviveEveryone()
        await self.myChannel.deleteMafiaChannel()

    async def reviveEveryone(self):
        for player in self.playersList:
            player :Player = player
            if player.isKilled:
                await self.revivePlayer(player)

    async def announceWinner(self):
        if self.isInnocentVictorious():
            await self.discordTextChannel.send("Innocents are the winners!")
        else:
            await self.discordTextChannel.send("Mafias are the winners!")

    async def announceWhoAreTheMafias(self):
        await self.discordTextChannel.send("These people are the mafias: ")
        for player in self.playersList:
            player :Player = player
            if player.isMafia():
                member = discord.utils.get(self.discordTextChannel.members, id=player.id)
                await self.discordTextChannel.send(f"{member.display_name}")
        

    def isInnocentVictorious(self):
        innocentCount = 0
        mafiaCount = 0
        for player in self.playersList:
            player :Player = player
            if player.isAlive():
                if player.isMafia():
                    mafiaCount += 1
                else:
                    innocentCount += 1

        return innocentCount > mafiaCount # TODO - innocent == mafia -> mafia wins

    async def revivePlayer(self, player :Player):
        member = discord.utils.get(self.discordTextChannel.members, id=player.id)
        self.unmuteMemberInChannel(member, self.discordTextChannel)
        if player.isMafia():
            self.unmuteMemberInChannel(member, self.myChannel.mafiaChannel)

    def deleteAllGameInfoFromDB(self):
        self.myChannel.removeDataFromDB()
        self.deleteAllPlayersFromDB()

    def deleteAllPlayersFromDB(self):
        for player in self.playersList:
            player :Player = player
            player.removeDataFromDB()

    

