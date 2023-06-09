""" 
Module with helper functions for the bot to use to check whether certain conditions are met before processing a command

"""

import discord
import MainGame.mySQLTables as mySQLTables

def isChannelInDB(discordTextChannel :discord.TextChannel):
    queryRes = mySQLTables.channelTable.selectFromTableWhere("*", "channelID", discordTextChannel.id)
    return queryRes != []
    
def isMafiaChannelInDB(potentialMafiaChannel :discord.TextChannel):
    queryRes = mySQLTables.channelTable.selectFromTableWhere("*", "mafiaChannelID", potentialMafiaChannel.id)
    print(f"QUERY IS MAFIA CHANNEL IN DB: {queryRes}")
    return queryRes != []

def getLinkedMainChannelWithMafiaChannel(mafiaChannel :discord.TextChannel) -> discord.TextChannel: 
    #TODO - relocate this function to a different module?
    queryRes = mySQLTables.channelTable.selectFromTableWhere("*", "mafiaChannelID", mafiaChannel.id)
    mainChannelID = queryRes[0][0]
    return discord.utils.get(mafiaChannel.guild.channels, id=mainChannelID)

def isPlayerOrMemberInDB(playerOrMember):
    queryRes = mySQLTables.playersTable.selectFromTableWhere("*", "playerID", playerOrMember.id)
    return queryRes != []

def isAnyMemberInDB(displayNameTuple, textChannel: discord.TextChannel):
    for name in displayNameTuple:
        member = discord.utils.get(textChannel.members, displayname=name)
        if isPlayerOrMemberInDB(member):
            return True
    
    return False


def createDisplayNamesList(
    listOfObjsWithAttDisplayName):
    lstToRet = []
    for objWithAttDisplayName in listOfObjsWithAttDisplayName:
        lstToRet.append(objWithAttDisplayName.display_name)
    return lstToRet

def areThereAnyDuplicateMemberInTextChannel(tc: discord.TextChannel):
    #TODO - relocate this function to a different module?
    displayNamesList = createDisplayNamesList(tc.members)
    return len(displayNamesList) != len(set(displayNamesList))



