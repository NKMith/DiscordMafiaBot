import discord
import MainGame.mySQLTables as mySQLTables

""" class Validator():
    def __init__():
        pass """

def isChannelInDB(discordTextChannel :discord.TextChannel):
    queryRes = mySQLTables.channelTable.selectFromTableWhere("*", "channelID", discordTextChannel.id)
    return queryRes != []
    
def isMafiaChannelInDB(potentialMafiaChannel :discord.TextChannel):
    queryRes = mySQLTables.channelTable.selectFromTableWhere("*", "mafiaChannelID", potentialMafiaChannel.id)
    return queryRes != []

def getLinkedMainChannelWithMafiaChannel(mafiaChannel :discord.TextChannel) -> discord.TextChannel: 
    #TODO - relocate this function to a different module?
    queryRes = mySQLTables.channelTable.selectFromTableWhere("*", "mafiaChannelID", mafiaChannel.id)
    mainChannelID = queryRes[0][0]
    return discord.utils.get(mafiaChannel.guild.channels, id=mainChannelID)