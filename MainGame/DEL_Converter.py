import discord
import MainGame.Table as Table
import MainGame.mySQLTables as mySQLTables
from MainGame.Player import Player

class Converter():
    """ 
    Creates game objects 
    """
    def __init__(self) -> None:
        pass

    def getPlayer(member :discord.member.Member):
        queryRes = mySQLTables.playersTable.selectFromTableWhere("*", "playerID", member.id)
        queryRes = queryRes[0] #Query res is a list of rows
        if queryRes == (): # Nothing in DB matches
            return Player(member)
        return Player(member, queryRes[1], queryRes[2])
    
    def getMyChannel(discordChannel :discord.TextChannel):
        pass