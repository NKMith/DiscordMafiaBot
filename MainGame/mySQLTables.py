import MainGame.Table as Table
Table.resetDB()


channelTable = Table.Table("ActiveChannels")
"""Channel ID | PlayersArray: array of IDs of players | phase | mafiaChannelID"""
channelTable.addField("channelID", "bigint unsigned PRIMARY KEY NOT NULL") 
channelTable.addField("playersArray", "JSON") # array of IDs of players
channelTable.addField("phase", "smallint unsigned")
channelTable.addField("mafiaChannelID", "bigint unsigned")
channelTable.createTable()


playersTable = Table.Table("ActivePlayers")
"""player ID | role | voteCount """
playersTable.addField("playerID", "bigint unsigned PRIMARY KEY NOT NULL")
playersTable.addField("role", "ENUM('Innocent', 'Mafia')")
playersTable.addField("voteCount", "smallint unsigned")
playersTable.createTable()