# Discord Mafia Bot (currently v.0.8.0)
Developed by NKMith


## License
I will allow distribution and any changes if you adhere to these conditions:
1. It is for personal or education use only
2. You may not modify the project in a way that can potentially harm someone in any sort of way (I'm most concerned with privacy breach)
3. Please credit me (NKMith) as one of the authors or as the "original author"


## Description
This project is a Discord Bot that allows players to play the popular Mafia Game in a Discord server. When the game starts, each player will get a role as either an Innocent or a Mafia. Around 1/4 of the players will be Mafias. Mafias will be added to a new private channel.

The game is divided into multiple phases, which there exists two types: Mafia phase and Citizen phase. During a Mafia phase, Mafias can discuss and vote on which citizen (including Mafias) to assasinate. During a Citizen phase, all players can discuss and vote on which citizen to execute. At the start of the next phase, the player with most votes will die. This player will still be able to read messages, but they will not be allowed to talk in any of the channels related to the game.

The game ends when either there aren't any more phases left (currently set as 2 for testing purposes) or when there are more or equal number of Mafias still alive than number of alive Innocents. In the former case, if there are more Innocents than Mafias alive, Innocents win. In the latter case, the Mafias win. 


## Rules / Commands
Commands have to start with the prefix '!'
In any commands where you have to put in a user's display name, if their display name includes any sort of emojis or special characters (including spaces), please encase them with douple quotes "" (eg. !command "display name")

- **!start**: add selected or all users in the current channel to the game
    - If you want to add all users to the game, just call the command without any arguments
    - If you want to add specific people to the game, please specify their display names after the command and separate the names with a space 
        - eg. !start NKMith fool2

- **!vote user_displayName**: vote for who to assassinate/execute. Each player gets 1 vote each phase

- **!next**: move on to the next phase. The player with most votes will be killed. Anyone can call this during any time during a phase

- **!finish**: forcefully finishes the game. This command may be removed once development finishes.
    

## Current limitations / Possible upgrades
- The game doesn't allow players to have duplicate display names (the game will check this and will not start if there are duplicate names)
    - Possible solution: if there are duplicate names, add a number behind their display names
- The maximum number of rounds is hardcoded when it should be in ratio with number of players (this is easy to fix, however)
- During a Mafia phase, a Mafia player can accidentally vote in the general channel, and the game will take it as a valid vote (which reveals their role)
- Display names aren't saved to the DB, resulting in having to search for it every time the game needs it
- Instead of voting a player via !vote command, the bot could send a message that relates certain emoji to each player, and then players could react to that specific message with certain emoji to vote for that player; when !next is called, the bot could simply get the count for each emoji (this fixes the problem of the a Mafia player accidentally voting in the general channel during a Mafia phase)

