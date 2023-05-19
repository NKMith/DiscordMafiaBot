""" 
Author: NKMith
Discord Mafia Bot v.0.1: A game running on Discord

"""
import MainGame.MafiaGame_SetUp as MafiaGame_SetUp
import discord
import MainGame.MafiaGameMain as MafiaGameMain
from env import *
import MainGame.Validator as Validator

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
    # TODO - MyChannel with same ID shouldn't be existing when this command is called
    if Validator.isChannelInDB(ctx.channel) or Validator.isMafiaChannelInDB(ctx.channel):
        ctx.channel.send("You already have a game ongoing related to this channel!")
        return
    
    game = MafiaGame_SetUp.MafiaGame_SetUp(ctx.channel, players_displayNames)
    game.giveAllPlayerRoles()
    game.printAllPlayers()
    # await game.notifyAllPlayersAboutRole()
    game.save()

    game = MafiaGameMain.MafiaGame(ctx.channel)
    await game.createMafiaChannel()
    game.save()


@bot.command(name="next")
async def nextRound(ctx :discord.ext.commands.Context):
    # TODO - Finish game if it hits certain phase
    # TODO - more mafias then innocents -> finish game

    channelIsAMafiaChannel = Validator.isMafiaChannelInDB(ctx.channel)
    if not Validator.isChannelInDB(ctx.channel) and not channelIsAMafiaChannel:
        ctx.channel.send("Invalid channel for 'next' command")
        return
    
    if channelIsAMafiaChannel:
        mainChannel = Validator.getLinkedMainChannelWithMafiaChannel(ctx.channel)
        game = MafiaGameMain.MafiaGame(mainChannel)
    else:
        game = MafiaGameMain.MafiaGame(ctx.channel)

    game = MafiaGameMain.MafiaGame(ctx.channel)
    await game.killPlayerWithMostVotesAndAnnounce()
    game.prepForNextRound()
    game.save()

@bot.command(name="vote")
async def voteWhoToKill(ctx :discord.ext.commands.Context, voteeDisplayName):
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
    game.save() #TODO - maybe just save the related players instead of saving the whole game?


@bot.command(name="finish")
async def finishGame(ctx :discord.ext.commands.Context):
    if not Validator.isChannelInDB(ctx.channel):
        ctx.channel.send("Invalid channel for 'finish' command")
        return
    game = MafiaGameMain.MafiaGame(ctx.channel)
    await game.finishGame()
    game.deleteAllGameInfoFromDB()

    


bot.run(BOT_TOKEN)

