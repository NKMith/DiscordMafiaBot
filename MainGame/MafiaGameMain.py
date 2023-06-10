""" 
Module with the main MafiaGame object that has most functionalities in the game
"""
from MainGame.Player import Player
from MainGame.RoleGiver import RoleGiver
from MainGame.MyChannel import MyChannel
import discord
import MainGame.Table
import MainGame.mySQLTables as mySQLTables
import json
import env
import time

class MafiaGame_Small():
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

    def printAllPlayers(self):
        for player in self.playersList:
            print(player.id)

    async def createMafiaChannel(self):
        """ 
        PRE: every player already got their role
        Create a secret channel only for mafias
        """
        guild = self.discordTextChannel.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
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

    def isInitialRound(self):
        return self.myChannel.phase == 0
    
    def isMafiaPhase(self):
        return self.myChannel.isMafiaPhase()
    
    def isCityPhase(self):
        return not self.myChannel.isMafiaPhase()
    
    def isLastRound(self):
        return self.myChannel.phase == env.LASTPHASENUM
    
    def areThereMoreMafiasLeftThanInnocents(self):
        mafiaCount = 0
        innocentCount = 0
        for player in self.playersList:
            player :Player = player 

            if player.isAlive():
                if player.isMafia():
                    mafiaCount += 1
                elif player.isInnocent():
                    innocentCount += 1

        return mafiaCount >= innocentCount
    
    
    def shouldGameEnd(self):
        return self.myChannel.phase > env.LASTPHASENUM or self.areThereMoreMafiasLeftThanInnocents()
    
    async def announceLastRound(self) -> None:
        await self.discordTextChannel.send("This is the last round!")

class MafiaGame_DB(MafiaGame_Small):
    def save(self):
        self.saveAllPlayers()
        self.myChannel.saveInfo()
    
    def saveAllPlayers(self):
        for player in self.playersList:
            player.saveInfo()
        print("Saved every player")

    def deleteAllGameInfoFromDB(self):
        self.myChannel.removeDataFromDB()
        self.deleteAllPlayersFromDB()

    def deleteAllPlayersFromDB(self):
        for player in self.playersList:
            player :Player = player
            player.removeDataFromDB()
    
class MafiaGame_Voting(MafiaGame_DB):
    async def votePlayerIfValid(self, voterUser :discord.member.Member, voteeDisplayName):
        voteeUser :discord.member.Member = discord.utils.get(self.discordTextChannel.members, display_name=voteeDisplayName)

        if voteeUser == None:
            await self.discordTextChannel.send(f"There is no player called {voteeDisplayName}!")
            return

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
        voterPlayer.setAlreadyVoted()
        voteePlayer.incrementVoteCount()

    def getPlayerWithID(self, id :int) -> Player:
        for player in self.playersList:   
            if player.id == id:
                return player
    
    async def announcePlayerVoteCounts(self):
        await self.discordTextChannel.send(f"This are the votes each player got in Phase {self.myChannel.phase}:")
        for player in self.playersList:
            player :Player = player
            member = discord.utils.get(self.discordTextChannel.members, id=player.id)
            await self.discordTextChannel.send(f"{member.display_name}: {player.voteCount}")

    def resetAllVotes(self):
        """Make everyone's voteCount 0 and reset their hasVoted boolean"""
        for player in self.playersList:
            player :Player = player
            player.voteCount = 0
            player.resetAlreadyVoted()

    async def announceWhichTeamWillStartVoting(self):
        if self.isCityPhase():
            await self.discordTextChannel.send("It is the citizens' time to vote")
        elif self.isMafiaPhase():
            await self.discordTextChannel.send("It is the mafias' time to vote")
            await self.myChannel.mafiaChannel.send("It is the mafias' time to vote")
       
class MafiaGame_WithKilling(MafiaGame_Voting):
    async def killPlayerWithMostVotesAndAnnounce(self):
        """
        PRE: playersList and MyChannel are set up
        Find and kill the player with most votes; if no one was voted, it kills no one
        If there are multiple players who have the same vote count, whoever is near the end of the playersList is killed
        """
        playerToKill :Player = self.playersList[0]
        for player in self.playersList:
            player :Player = player
            print(f"{player.id}'s vote count is {player.voteCount}")
            if player.voteCount >= playerToKill.voteCount and player.isAlive():
                playerToKill = player

        print(f"PLAYER TO KILL: {playerToKill.id}")

        if playerToKill.voteCount == 0:
            await self.discordTextChannel.send("No one has been voted, therefore everyone lives!")
        else:
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

    async def reviveEveryone(self):
        for player in self.playersList:
            player :Player = player
            if player.isKilled:
                await self.revivePlayer(player)
    
    async def revivePlayer(self, player :Player):
        member = discord.utils.get(self.discordTextChannel.members, id=player.id)
        await self.unmuteMemberInChannel(member, self.discordTextChannel)
        if player.isMafia():
            await self.unmuteMemberInChannel(member, self.myChannel.mafiaChannel)

    async def unmuteMemberInChannel(self, userToMute :discord.member.Member, channelToMute):
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        await channelToMute.set_permissions(userToMute, overwrite=overwrite)


#Has all the finish-related methods
class MafiaGame(MafiaGame_WithKilling):
    def prepForNextRound(self):
        """Increment phase and reset votes"""
        self.myChannel.incrementPhase()
        self.resetAllVotes()

    async def finishGameAndDeleteData(self):
        await self.finishGame()
        self.deleteAllGameInfoFromDB()

    async def finishGame(self):
        """ Does not delete data from DB """
        await self.announceWinner()
        await self.announceWhoAreTheMafias()
        await self.reviveEveryone()
        await self.myChannel.deleteMafiaChannel()

    async def announceWinner(self):
        if self.areThereMoreMafiasLeftThanInnocents():
            await self.discordTextChannel.send("Mafias are the winners!")
        else:
            await self.discordTextChannel.send("Innocents are the winners!")

    async def announceWhoAreTheMafias(self):
        announceStr = "These people are the mafias: "
        for player in self.playersList:
            player :Player = player
            if player.isMafia():
                member = discord.utils.get(self.discordTextChannel.members, id=player.id)
                announceStr += member.display_name

        await self.discordTextChannel.send(announceStr)
