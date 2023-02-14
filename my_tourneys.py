# project structure
# KIVYMD app to make simple tourneys
# Start with simple random pairing + keep track of previous pairing for next round
# Simple database to keep track of informations and extract results in Excel ?
# Implement app in store
# Then :
# swiss round system but make it scalable for more
# visualisation for tournaments, pairing, points
# Class system for tourneys to make it customisable later

import random, sqlite3, datetime


con = sqlite3.connect("tourney_db.db")
cur = con.cursor()


def db_create():
    # 4 tables for relation : tourneys, players, matches and player_matches
    # tourneys is the local save of all tourney keys
    # players are a list of all players with a unique ID
    # matches allows to follow on the matches and get unique ID
    # player_matches stores the result for each player and allows to retrieve and calculate results
    # The key to this data schema is understanding constraints, foreign keys and compound primary key


    cur.execute(
        """CREATE TABLE players(
        p_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        p_name NOT NULL, 
        p_surname NOT NULL
        )"""
    )

    cur.execute(
        """CREATE TABLE matches(
        m_id INTEGER PRIMARY KEY AUTOINCREMENT,
        t_id NOT NULL,
        round INT NOT NULL
        )"""
    )

    cur.execute(
        """CREATE TABLE player_matches(
        m_id INT NOT NULL FOREIGN KEY REFERENCES matches(m_id), 
        p_id INT NOT NULL FOREIGN KEY REFERENCES players(p_id), 
        p_result,
        p_score, 
        CONSTRAINT PK_matchPlayer PRIMARY KEY (m_id, p_id)
        )"""
    )

    cur.execute(
        """CREATE TABLE tourneys(
        t_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        t_type, 
        t_date, 
        t_name
        )"""
    )
    con.commit()


def enroll_players(p: list) -> bool:
    # check the list for format
    # check for player already existing ?
    # error messages if needed

    cur.executemany(
        """INSERT INTO  players(p_name, p_surname) VALUES (?, ?)""",
        p
    )
    con.commit()
    return True

def create_tourney(t_type: str, t_name):
    """
    initialise tournament
    """
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    params = (t_type, today, t_name)
    command = """INSERT INTO tourneys(?, ?, ?)"""
    cur.execute(command, params)
    con.commit()

    return f"Tournament {t_name} was created"


def get_tourneys_list():
    """ Returns the list of tournaments and their details"""

    cur.execute("""SELECT * from tourneys""")
    return cur.fetchall()


def get_player_id(infos: list) -> list:
    # find players ID with their name in case we need it
    names = cur.execute("""SELECT * FROM players WHERE (p_name =? AND p_surname= ?)""", infos)
    return names.fetchall()


def read_players() -> list:
    """ get all registered players informations """

    call = cur.execute("""SELECT * FROM players""")
    return call.fetchall()


def rand_pairing(players: list) -> (list, int):
    """
    Randomize players and pair them
    """
    random.shuffle(players)
    bye_player_name = players.pop() if len(players) % 2 else None
    matches = []

    while players:
        match = [players.pop() for x in range(2)]
        matches.append(match)
    return matches, bye_player_name


def create_match(pairing: list, t_id: int, round: int, bye_player: int) -> list:
    """
    feeds the matches table for the matches of this round
    returns the matches ID for this round
    """

    matches = [(t_id, round) for x in range(len(pairing))]
    if bye_player:
        matches.append((t_id, round))

    cur.executemany(
        f"""INSERT INTO matches(t_id, round) VALUES (?, ?)""",
        matches
    )
    round_id = (t_id, round)
    matches_ids = "SELECT m_id FROM matches WHERE t_id = ? AND round = ?"
    return cur.execute(matches_ids, round_id).fetchall()


def player_matches(m_ids: list, pairing: list, bye_player: int) -> None:
    """
    feed the players id for the matches created previously
    """
    if bye_player:
        pairing.append((0,0))

    matches = []
    for x in range(len(m_ids)):
        matches.append(m_ids[x], pairing[x][0])
        matches.append(m_ids[x], pairing[x][1])

    p_matches = """INSERT INTO player_matches(m_id, p_id) VALUES (?, ?) """
    cur.execute(p_matches, matches)


def table_pairing(pairs: list) -> list:
    """
    Takes a list of player id pairings and return tuples of names for KIVYMDtable
    format [[p1, p2]]
    """
    pairing = []
    # TODO check if this code is ok for feeding the matches table
    # Need to ID the tourney, transform into OOP ?

    for pair in pairs:
        players_names = cur.execute("""SELECT p_name, p_surname FROM players WHERE  p_id = ? OR p_id = ?""", pair)
        pairing.append(tuple(players_names))
    con.commit()

    return pairing


def players_list(t_id: int) -> list:
    """
    takes a tournament id and gives back the list of players
    """
    command = """
    SELECT p_id 
    FROM players_matches 
    INNER JOIN matches
    ON player_matches.m_id = matches.m_id
    WHERE t_id = ?
    """
    return cur.execute(command, t_id).fecthall()

def pairing_process(t_id: int, round: int) -> (list, list):
    """
    Main process calling all pairing function in order
    """
    # Create a list of IDs  from players list
    # ToDO : make system to follow up on rounds
    # use function to create pairing from ids
    players_pool = players_list(t_id)
    pairing, bye_player = rand_pairing(players_pool)
    round_matches = create_match(pairing, t_id, round, bye_player)
    player_matches(round_matches, pairing, bye_player)

    # get bye player text name from table and use function to convert pairing list from ids to actual string.
    bye_player_name = cur.execute(
        """SELECT p_name, p_surname FROM players WHERE  p_id = ?""",
        [bye_player]
    ).fetchall()
    table_show = table_pairing(pairing)

    return table_show, bye_player_name

### Old round pairin function
def round_pairing(players: list, previous_matches: list, bye_list: list) -> (list, str):
    """
    remove a random player if uneven number of players
    make sure he wasn't already 'bye' previous round
    """
    # # TODO : is this function still relevant with new structure ?
    # # First ID the bye player and pop it off the list
    # rand_num = random.randint(0, len(players)-1)
    # if len(players) % 2:
    #     while players[rand_num] in bye_list:
    #         if rand_num < (len(players)-1):
    #             rand_num += 1
    #         else:
    #             rand_num -= 1
    #     bye_player_name = players.pop(rand_num)
    #     print("bye : ", bye_player_name)
    # else:
    #     bye_player_name = None
    #
    # # Then let's make the pairings and avoid having the same matches as before
    # # we don't handle the case when a pairing already exists but it's the last pairing !
    # # previous matches not identified for reversed lists : [A, B] != [B,A]
    # # Error : list index out of range
    # pair_2 = 0
    # pairings = list()
    # print(players)
    # while players:
    #     while [players[0], players[pair_2]] in previous_matches:
    #         pair_2 += 1
    #     pairings.append([players.pop(0), players.pop(pair_2)])
    #     print(pairings)
    #     pair_2 = 0
    #     print(players)
    # return pairings, bye_player_name


def score_sort(scores: list) -> list:
    """
    create a sorted list of players where index 0 is the highest
    project : create my own algorythm to scale for big tournaments
    """
    return sorted(scores, key=lambda x: x[1], reverse=True)


def players_scores(t_id: int):
    """ give current scores for tourney"""

    query = """get scores from the matches tables"""
    players = ["list of players id to loop through"]
    # loop through players executing a query to get their score
    scores = cur.execute(query, t_id)

    return scores.fetchall()


def enter_results(results: list) -> str:
    """
    Feeding the matches table with the result entered by user
    Format must be : [(p1_score, p2_score, t_id, p_id_1, p_id_2 ), ... )
    """

    cur.executemany(
        """
        UPDATE matches 
        SET p1_score = ?, p2_score = ?  
        WHERE t_id = ? AND p1_id = ? AND p2_id = ?  
        """,
        results
    )
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
    # kivy table needs a tuple with all the row data : player1, player2...
    # print(pairing_process(1))
    print(cur.execute("""SELECT * FROM matches""").fetchall())
    results = [(1, 2, 1, 4, 7),
               (2, 0, 1, 5, 1),
               (1, 1, 1, 2, 6)]
    enter_results(results)
    print(cur.execute("""SELECT * FROM matches""").fetchall())

