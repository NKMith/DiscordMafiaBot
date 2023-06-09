""" 
Author: NKMith
Discord Mafia Bot v.0.8: Runs a mafia game in Discord

"""
import MainGame.MafiaGame_SetUp as MafiaGame_SetUp
import discord
import MainGame.MafiaGameMain as MafiaGameMain
from env import *
import MainGame.Validator as Validator
import time
#from MainGame.AsyncMafiaGameConstructor import AsyncMafiaGameConstructor

from discord.ext import commands #import discord
from dotenv import load_dotenv
myIntents = discord.Intents.all()
bot = commands.Bot(intents = myIntents, command_prefix=['!'])

def is_user_god(user) -> bool:
    return user.id == GOD_ID

def is_user_bot(user) -> bool:
    return user == bot.user
    
def convertMonthToText(month):
    return ["January", "February", "March", "April", "May", "June", "July",
            "August", "September", "October", "November", "December"][month-1]



@bot.event
async def on_ready():
    #RESET DB
    print(f"Bot {bot.user} has booted! Resetting DB.")

@bot.event
#Intents: messages
async def on_message(message :discord.Message):
    print(f"{message.author.display_name}: {message.content}")
    if is_user_bot(message.author): # checks that the bot is not responding to itself
       return

    # default on_message contains a call to this coroutine (process_commands), but 
    # when you override it with your own on_message, you need to call it yourself.
    await bot.process_commands(message) #only needed in on_message


# ctx == class discord.ext.commands.Context ; Represents the context in which a command is being invoked under.
@bot.command(name="pretend_bot", help="<guildName> <channelName> <messageContent>")
async def pretend_bot(ctx, guildName, channelName, messageContent):
    if is_user_god(ctx.author) and type(ctx.channel) == discord.DMChannel:
        guild = discord.utils.get(bot.guilds, name=guildName) #Intents: guilds
        channel = discord.utils.get(guild.channels, name=channelName)
        await channel.send(messageContent)

""" 
Set up and start the Mafia game
"""
@bot.command(name="start")
async def startGame(ctx :discord.ext.commands.Context, *players_displayNames):
    # Game starts with phase 0, where Mafias get to vote who to kill
    if Validator.isChannelInDB(ctx.channel) or Validator.isMafiaChannelInDB(ctx.channel):
        await ctx.channel.send("You already have a game ongoing related to this channel!")
        return
    
    if Validator.areThereAnyDuplicateMemberInTextChannel(ctx.channel):
        await ctx.channel.send("There are users in this channel with same display names...For now, this is not allowed.")
        return

    game = MafiaGame_SetUp.MafiaGame_SetUp(ctx.channel, players_displayNames)

    await game.announceWhichPlayersWerentAdded()
    game.giveAllPlayerRoles()
    game.printAllPlayers()
    # await game.notifyAllPlayersAboutRole()
    game.save()

    game = MafiaGameMain.MafiaGame(ctx.channel)
    await game.createMafiaChannel()
    game.save()
    await game.announceWhichTeamWillStartVoting()

@bot.command(name="finish")
async def finishGame(ctx :discord.ext.commands.Context):
    if not Validator.isChannelInDB(ctx.channel):
        await ctx.channel.send("Invalid channel for 'finish' command")
        return
    

    await ctx.channel.send("The game is finished!")
    game = MafiaGameMain.MafiaGame(ctx.channel)
    await game.finishGameAndDeleteData()

@bot.command(name="next")
async def nextRound(ctx :discord.ext.commands.Context):
    channelIsAMafiaChannel = Validator.isMafiaChannelInDB(ctx.channel)

    # if it's a channel not related to any game
    if not Validator.isChannelInDB(ctx.channel) and not channelIsAMafiaChannel:
        await ctx.channel.send("Invalid channel for 'next' command")
        return
    
    # get game object
    if channelIsAMafiaChannel:
        mainChannel = Validator.getLinkedMainChannelWithMafiaChannel(ctx.channel)
        game = MafiaGameMain.MafiaGame(mainChannel)
    else:
        game = MafiaGameMain.MafiaGame(ctx.channel)


    if game.isMafiaPhase() and not channelIsAMafiaChannel:
        await ctx.channel.send("'next' command should be called in the mafia channel when it's during a Mafia phase!")
        return
    elif game.isCityPhase() and channelIsAMafiaChannel:
        await ctx.channel.send("'next' command should be called in the city channel when it's during a City phase!")
        return
    
    if game.isLastRound():
        await game.announceLastRound()

    await game.killPlayerWithMostVotesAndAnnounce()
    await game.announcePlayerVoteCounts()

    if game.shouldGameEnd():
        await game.finishGameAndDeleteData()
        return
    

    game.prepForNextRound()
    await game.announceWhichTeamWillStartVoting()
    game.save()

@bot.command(name="vote")
async def voteWhoToKill(ctx :discord.ext.commands.Context, voteeDisplayName):
    # !!! people with weird display names: "" around their name when using the command
    channelIsAMafiaChannel = Validator.isMafiaChannelInDB(ctx.channel)
    if not Validator.isChannelInDB(ctx.channel) and not channelIsAMafiaChannel:
        await ctx.channel.send("Invalid channel for 'vote' command")
        return
    
    if channelIsAMafiaChannel:
        mainChannel = Validator.getLinkedMainChannelWithMafiaChannel(ctx.channel)
        game = MafiaGameMain.MafiaGame(mainChannel)
    else:
        game = MafiaGameMain.MafiaGame(ctx.channel)

    await game.votePlayerIfValid(ctx.author, voteeDisplayName)
    game.save()


@bot.command(name="revive") # Command just for development
async def reviveCommand(ctx):
    game = MafiaGameMain.MafiaGame(ctx.channel)
    await game.reviveEveryone()

@bot.command(name="deleteAllMafiaRooms") # Command just for development
async def deleteAllMafiaRooms(ctx :discord.ext.commands.Context):
    if ctx.author.id != GOD_ID:
        return
    mafiaChannel :discord.TextChannel = discord.utils.get(ctx.guild.channels, name="mafiaroom")
    while mafiaChannel != None:
        await mafiaChannel.delete()
        mafiaChannel :discord.TextChannel = discord.utils.get(ctx.guild.channels, name="mafiaroom")


bot.run(BOT_TOKEN)

