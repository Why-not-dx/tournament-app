# project structure
# KIVYMD app to make simple tourneys
# Start with simple random pairing + keep track of previous pairing for next round
# Simple database to keep track of informations and extract results in excel ?
# Implement app in store
# Then :
# swiss round system but make it scalable for more
# visualisation for tournaments, pairing, points
# Class system for tourneys to make it customisable later

import random
import sqlite3

con = sqlite3.connect("tourney_db.db")
cur = con.cursor()


def db_create():
    # 3 tables for relation : tourneys, players and matches
    #tourneys is the local save of all tourney keys
    # players are a list of all players with a unique ID
    # matches allows to follow on the matches and get points / results from it

    cur.execute(
        """CREATE TABLE players(
        p_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        p_name, 
        p_surname)"""
    )
    cur.execute(
        """CREATE TABLE matches(
        t_id, 
        p1_id, p2_id, 
        p1_score, p2_score)"""
    )
    cur.execute(
        """CREATE TABLE tourneys(
        t_id, 
        tourney_type, 
        tourney_date, 
        tourney_name)"""
    )
    con.commit()


def enroll_players(p: list)->bool:
    #check the list for format
    #check for player already existing ?
    #error messages if needed

    cur.executemany(
        """INSERT INTO  players(p_name, p_surname) VALUES (?, ?)""",
        p)
    con.commit()
    return True


def get_player_id(infos) -> list:
    # find players ID with their name in case we need it
    names = cur.execute("""SELECT * FROM players WHERE (p_name =? AND p_surname= ?)""", infos)
    return names.fetchall()


def read_players() -> list:
    """ return list of contestants"""
    call = cur.execute("""SELECT * FROM players""")
    return call.fetchall()


def rand_pairing(players: list) -> (list, str):
    random.shuffle(players)
    bye_player_name = players.pop() if len(players) % 2 else None
    matches = []

    while players:
        match = [players.pop() for x in range(2)]
        matches.append(match)
    return matches, bye_player_name


def table_pairing(pairs: list) -> list:
    # Takes a list of player id pairings and return tuples of names for KIVYMDtable
    # format [[p1, p2]]
    pairing = []
    for pair in pairs:
        players_names = cur.execute("""SELECT p_name, p_surname FROM players WHERE  p_id = ? OR p_id = ?""", pair)
        pairing.append(tuple(players_names))

    return pairing


def pairing_process() -> (list, list):
    # TODO : call to the tourney ID to get players from this tourney + keep track of the previous matches for next match making
    players = [p[0] for p in read_players()]
    pairing, bye_player = rand_pairing(players)
    bye_player_name = cur.execute("""SELECT p_name, p_surname FROM players WHERE  p_id = ?""", [bye_player]).fetchall()
    table_show = table_pairing(pairing)

    return table_show, bye_player_name


def round_pairing(players: list, previous_matches: list, bye_list: list) -> (list, str):
    """remove a random player if uneven number of players
    make sure he wasn't already 'bye' previous round"""
    # First ID the bye player and pop it off the list
    rand_num = random.randint(0, len(players)-1)
    if len(players) % 2:
        while players[rand_num] in bye_list:
            if rand_num < (len(players)-1):
                rand_num += 1
            else:
                rand_num -= 1
        bye_player_name = players.pop(rand_num)
        print("bye : ", bye_player_name)
    else:
        bye_player_name = None

    # Then let's make the pairings and avoid having the same matches as before
    # we don't handle the case when a pairing already exists but it's the last pairing !
    # previous matches not identified for reversed lists : [A, B] != [B,A]
    #Error : list index out of range
    pair_2 = 0
    pairings = list()
    print(players)
    while players:
        while [players[0], players[pair_2]] in previous_matches:
            pair_2 += 1
        pairings.append([players.pop(0), players.pop(pair_2)])
        print(pairings)
        pair_2 = 0
        print(players)
    return pairings, bye_player_name


def read_scores() -> list:
    #USELESS WITH NEW SYSTEM
    """get a dict of the scores and players ID"""
    call = cur.execute("""SELECT name, score FROM Tournament""")
    return call.fetchall()


def match_result(results: list)->str:
    """2 scenarios : all the results in one go ot just a result / edit| NEED TO KEEP ROUNDS INFORMATIONS"""
    cur.executemany("""UPDATE Tournament SET win=?, loss=?, draw=? WHERE name= ? """, results)
    con.commit()
    return "Scores updated"


def score_sort(scores: list) -> list:
    """
    create a sorted list of players where index 0 is the highest
    project : create my own algorythm to scale for big tournaments
    """
    return sorted(scores, key=lambda x: x[1], reverse=True)

def update_points() -> str:
    #USELESS NOW WITH NEW TABLE FORMAT ?
    scores = cur.execute("""SELECT name, win, draw FROM Tournament""").fetchall()
    points = [[play[1]*2 + play[2], play[0]] for play in scores]

    cur.executemany("""UPDATE Tournament SET score=? WHERE name= ? """, points)
    con.commit()

    return "Points updated"
# for next rounds, need test to have players have different opponents (not in previous pairing list)
# Maybe make this the first pairing func then create a follow-up pairing with results and previous matches


if __name__ == "__main__":
    # db_create()
    # info_list = [
    #     ('Anthony', 'Guts'),
    #     ('Joey', 'Ryoma'),
    #     ('Mai', 'Valentine'),
    #     ("Ryo", "Saeba"),
    #     ("Ranni", "Zewich"),
    #     ("Neils", "Bohred"),
    #     ("Jensen", "Kimmit")
    # ]
    # enroll_players(info_list)
    # play_list = read_players()
    # id_list = [p[0] for p in play_list]
    # print(id_list)
    # pairing_id = rand_pairing(id_list)
    # print(pairing_id)
    # print(table_pairing(pairing_id[0]))
    #kivy table needs a tuple with all the row data : player1, player2...
    print(pairing_process())

