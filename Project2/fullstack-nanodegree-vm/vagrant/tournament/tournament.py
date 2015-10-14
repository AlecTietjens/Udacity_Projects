#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#
# Author: Alec Tietjens
# Date: 09/28/2015

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


"""Remove all the player records from the database."""
def deleteMatches():
    conn = connect()
    c = conn.cursor()
    c.execute("TRUNCATE TABLE Match;")
    conn.commit()
    conn.close()

"""Remove all the player records from the database."""
def deletePlayers():
    conn = connect()
    c = conn.cursor()
    c.execute("TRUNCATE TABLE Player;")
    c.execute("TRUNCATE TABLE Standings;")
    conn.commit()
    conn.close()

"""Returns the number of players currently registered."""
def countPlayers():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * FROM Player;")
    count = c.rowcount
    conn.commit()
    conn.close()
    return count
		
"""Adds a player to the tournament database.
	
    Args:
      name: the player's full name (need not be unique).
"""
def registerPlayer(name):
    conn = connect()
    c = conn.cursor()
    """Insert player into Player table"""
    c.execute("INSERT INTO Player(name) VALUES (%s);", (name,))
    c.execute("SELECT id FROM Player WHERE name=%s", (name,))
    
    """Insert player into Standings table"""
    playerid = c.fetchone()[0]
    c.execute("INSERT INTO Standings(playername, playerid) VALUES(%s, %s);", (name, playerid))
    conn.commit()
    conn.close() 

"""Returns a list of the players and their win records, sorted by wins.

    Returns:
      A SORTED BY WINS list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
def playerStandings():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * FROM Standings ORDER BY WINS;")
	
    """create list and add players and their standing to it"""
    player_list = []
    for x in range(0, c.rowcount):
        player = c.fetchone()
        player_list.append([player[2], player[1], player[3], player[4]])
    conn.commit()
    conn.close()
    return player_list

"""Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
def reportMatch(winner, loser):
    conn = connect()
    c = conn.cursor()

    """Report the match"""
    c.execute("INSERT INTO Match(WinnerID, LoserID) VALUES(%s, %s);", (winner, loser))
	
    """Update Standings - Update record for the winner"""
    c.execute("SELECT Wins, Matches FROM Standings WHERE PlayerID=%s;", (winner,))
    winner_standings = c.fetchone()
    c.execute("UPDATE Standings SET Wins=%s, Matches=%s WHERE PlayerID=%s;", (winner_standings[0]+1,winner_standings[1]+1, winner))
    
    """Update Standings - Update record for the loser"""
    c.execute("SELECT Matches FROM Standings WHERE PlayerID=%s;", (loser,))
    loser_standings = c.fetchone()
    c.execute("UPDATE Standings SET Matches=%s WHERE PlayerID=%s;", (loser_standings[0]+1, loser))

    count = c.rowcount
    conn.commit()
    conn.close()
 
"""Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """ 
def swissPairings():
    standings_list = playerStandings()
    swiss_pairings = []
    
    for x in range(0, len(standings_list), 2):
        player1 = standings_list[x]
        player2 = standings_list[x+1]
        swiss_pairings.append((player1[0], player1[1], player2[0], player2[1]))

    return swiss_pairings