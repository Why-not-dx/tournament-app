# project structure
# KIVYMD app to make simple tourneys
# Start with swiss round system but make it scalable for more
# Simple database to handle things over time
# visualisation for tournaments, pairing, points
# Class system for tourneys to make it customisable later

import random
import sqlite3

registering = ["Joey", "Mai", "Ken", "Marek", "Cyrius", "Alexis"]
scores = {"Joey": 1, "Mai": 2, "Ken": 2, "Marek": 0, "Cyrius": 0, "Alexis": 1}

# TODO - add a point counter so that you pair players with the same points
# conclusion -> use sqlite for easy queries
con = sqlite3.connect("tourney_db.db")
cur = con.cursor()


def db_create():
    cur.execute("""CREATE TABLE Tournament(id, name, surname, score, win, loss, draw)""")
    cur.execute("CREATE TABLE matchups(matchup, player1, player2)")

    info_list = [
        (1, 'Anthony', 'Guts'),
        (2, 'Joey', 'Ryoma'),
        (3, 'Mai', 'Valentine'),
        (4, "Ryo", "Saeba"),
        (5, "Ranni", "Zewich"),
        (6, "Neils", "Bore"),
        (7, "Jensen", "Kimmit")
    ]

    cur.executemany(("""INSERT INTO Tournament VALUES (?, ?, ?, 0, 0, 0, 0)"""), info_list)

    # print(list(players_table))
    players_table = cur.execute("""SELECT * from Tournament""")
    print(players_table.fetchall())
    con.commit()


def update_points() -> str:
    scores = cur.execute("""SELECT name, win, draw FROM Tournament""").fetchall()
    points = [[play[1]*2 + play[2], play[0]] for play in scores]

    cur.executemany("""UPDATE Tournament SET score=? WHERE name= ? """, points)
    con.commit()

    return "Points updated"

def read_contestants()->list:
    """ return list of contestants"""
    call = cur.execute("""SELECT name, surname FROM Tournament""")
    return call.fetchall()

def update_score(results: list)->str:
    """2 scenarios : all the results in one go ot just a result / edit| NEED TO KEEP ROUNDS INFORMATIONS"""
    cur.executemany("""UPDATE Tournament SET win=?, loss=?, draw=? WHERE name= ? """, results)
    con.commit()
    return "Scores updated"


def score_sort(scores: dict) -> list:
    """
    create a sorted list of players where index 0 is the highest
    project : create my own algorythm to scale for big tournaments
"""
    standings = [[x, y] for x, y in scores.items()]
    return sorted(standings, key=lambda x: x[1], reverse=True)

# for next rounds, need test to have players have different opponents (not in previous pairing list)
# Maybe make this the first pairing func then create a follow-up pairing with results and previous matches


def pairing(players: list) -> (list, str):
    random.shuffle(players)
    player_by_name = players.pop() if len(players) % 2 else None
    matches = []

    while players:
        match = [players.pop() for x in range(2)]
        matches.append(match)
    return matches, player_by_name


def rounds(prev_match: list, standings: list) -> list:
    """
    take standings, generate new matches + check that those pair didn't already exist
    create the new matches list
    """
    print(prev_match, standings)
    return []

if __name__ == "__main__":
    rez = [(0, 1, 0, "Anthony"),
           (1, 0, 0, "Joey"),
           (0, 0, 1, "Mai"),
           (1,0,1, "Ranni"),
           (0, 1, 0, "Ryo"),
           (1, 0, 1, "Neils"),
           (2, 1, 0, "Jensen")
           ]
    update_score(rez)
    players_table = cur.execute("""SELECT * from Tournament""")
    print(players_table.fetchall())
    print(update_points())
    players_table = cur.execute("""SELECT * from Tournament""")
    print(players_table.fetchall())
    #db_create()
    #print(read_contestants())
    # test = pairing(registering)
    # print(test)
    # standings = score_sort(scores)
    # print(standings)
    # print([standings.pop() for x in range(2)])
    pass
