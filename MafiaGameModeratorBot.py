""" 
Author: NKMith
Discord Mafia Bot v.0.1: A game running on Discord

"""
import MainGame.MafiaGame_SetUp as MafiaGame_SetUp
import discord
import random
import MainGame.MafiaGameMain as MafiaGameMain
from env import *
from MainGame.Player import Player

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
    game = MafiaGame_SetUp.MafiaGame_SetUp(ctx.channel, players_displayNames)
    game.giveAllPlayerRoles()
    game.save()
    game.printAllPlayers()
    await game.notifyAllPlayersAboutRole()

@bot.command(name="next")
async def nextRound(ctx :discord.ext.commands.Context):
    # TODO - !next should be invoked from the Mafia channel or the main game channel
    # TODO - kill the player with most votes
    # TODO - !Reset all vote counts

    # recreate mafia game object and read info from DB using channel ID as key
    # create a separate channel in the server for mafias, only allow mafias in it
    # make mafias vote to who to kill
    # kill that one guy
    game = MafiaGameMain.MafiaGame(ctx.channel)
    if game.isInitialRound():
        await game.createMafiaChannel()
    else:
        game.killPlayerWithMostVotes()

@bot.command(name="vote")
async def voteWhoToKill(ctx :discord.ext.commands.Context, voteeDisplayName):
    # TODO - votes have to be from the Mafia channel or the main game channel
    # TODO - Each person should get 1 vote each phase
    voteeMember = discord.utils.get(ctx.guild.members, display_name=voteeDisplayName)
    voteePlayer = Player(voteeMember)
    voteePlayer.getVoted()
    



bot.run(BOT_TOKEN)

