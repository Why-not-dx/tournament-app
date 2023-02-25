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

# TODO : a next round function to go to next round and take previous pairing into account
# Also, need to work on the way to add players / add them to a tourney. List handling, clicking on lists in app ...


def db_create():
    """ Creates 4 tables : tourneys, players, matches and player_matches
    - tourneys is the local save of all tourney keys,
    - players are a list of all players with a unique ID,
    - matches allows to follow on the matches and get unique ID,
    - player_matches stores the result for each player and allows to retrieve and calculate results,
    - The key to this data schema is understanding constraints, foreign keys and compound primary key """


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
        m_id INT NOT NULL, 
        p_id INT NOT NULL,
        p_result,
        p_score,
        FOREIGN KEY (p_id) REFERENCES players(p_id), 
        FOREIGN KEY (m_id) REFERENCES matches(m_id),
        CONSTRAINT PK_matchPlayer PRIMARY KEY (m_id, p_id)
        )"""
    )

    cur.execute(
        """CREATE TABLE tourneys(
        t_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        t_type NOT NULL, 
        t_date, 
        t_name UNIQUE NOT NULL 
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


def create_tourney(t_type: str, t_name: str) -> int:
    """
    initialise tournament and return the ID of the generated tournament
    """
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    params = (t_type, today, t_name,)
    command = """INSERT INTO tourneys(t_type, t_date, t_name) VALUES (?, ?, ?)"""
    cur.execute(command, params)
    con.commit()

    query = f"SELECT t_id FROM tourneys WHERE t_name = ?"

    return cur.execute(query, (t_name,)).fetchall()[0][0]


def get_tourneys_list():
    """ Returns the list of tournaments and their details"""

    cur.execute("""SELECT * from tourneys""")
    return cur.fetchall()


def get_players_id(infos: list) -> list:
    # find players ID with their name in case we need it
    names = cur.execute("""SELECT * FROM players WHERE (p_name =? AND p_surname= ?)""", infos)

    return names.fetchall()


def read_players() -> list:
    """ get all registered players informations """

    call = cur.execute("""SELECT * FROM players""")
    return call.fetchall()


def rand_pairing(players: list, prev_bye: int = None) -> (list, int):
    """
    Randomize players and pair them
    """

    random.shuffle(players)
    while players[-1] == prev_bye:
        random.shuffle(players)

    bye_player_name = players.pop() if len(players) % 2 else None
    matches = []

    while players:
        match = [players.pop() for x in range(2)]
        matches.append(match)
    return matches, bye_player_name


def create_match(pairing: list, t_id: int, t_round: int, bye_player: int) -> list:
    """
    feeds the matches table for the matches of this round
    returns the matches ID for this round
    """

    matches = [(t_id, t_round) for x in range(len(pairing))]
    if bye_player:
        matches.append((t_id, t_round))

    cur.executemany(
        f"""INSERT INTO matches(t_id, round) VALUES (?, ?)""",
        matches
    )
    round_id = (t_id, t_round)
    matches_ids = "SELECT m_id FROM matches WHERE t_id = ? AND round = ?"
    return cur.execute(matches_ids, round_id).fetchall()


def player_matches(m_ids: list, pairing: list, bye_player: int) -> None:
    """
    feed the players id for the matches created previously
    """

    # We need to adapt the matches list so that the bye player doesn't have an opponent.
    # In case of bye player, the last match is not filled in the loop so that we add him only.
    matches = []
    bye_count = 0
    if bye_player:
        bye_count = 1

    for x in range(len(m_ids) - bye_count):
        matches.append((m_ids[x][0], pairing[x][0]))
        matches.append((m_ids[x][0], pairing[x][1]))

    if bye_player:
        matches.append((m_ids[len(m_ids) - 1][0], bye_player))

    p_matches = """INSERT INTO player_matches(m_id, p_id) VALUES (?, ?) """
    cur.executemany(p_matches, matches)


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
    return cur.execute(command, t_id).fetchall()


def pairing_process(t_id: int, t_round: int, players: list) -> (list, list):
    """
    Main process calling all pairing function in order
    """

    pairing, bye_player = rand_pairing(players)
    round_matches = create_match(pairing, t_id, t_round, bye_player)
    player_matches(round_matches, pairing, bye_player)

    # get bye player text name from table and use function to convert pairing list from ids to actual string.
    bye_player_name = cur.execute(
        """SELECT p_name, p_surname FROM players WHERE  p_id = ?""",
        [bye_player]
    ).fetchall()
    table_show = table_pairing(pairing)

    return table_show, bye_player_name


def get_previous_pairing(t_id: int, t_round: int) -> (list, tuple):
    """ takes informations about match and round to give back list of previous pairing (players ids)"""
    # select m_ids from good t_id and round in matches
    # select m_id and p_id from player_matches where m_ids = previous selection
    # convert this list into a list of pairing (in tuples so it's unordered).

    infos = (t_id, t_round,)
    player_matches = "" \
                     "SELECT m_id, p_id " \
                     "FROM player_matches " \
                     "WHERE m_id IN( " \
                     "    SELECT m_id " \
                     "    FROM matches " \
                     "    WHERE t_id = ? " \
                     "    AND round = ? ) "

    match_list = cur.execute(player_matches, infos).fetchall()
    match_pairings = {match: tuple(player for match_id, player in match_list if match_id == match) for match, _ in match_list}
    prev_pairings = list(match_pairings.values())
    print(prev_pairings)
    prev_bye_player = next(filter(lambda x: len(x) == 1, prev_pairings))[0]

    return prev_pairings, prev_bye_player


def next_round_pairing(t_id: int, t_round: int) -> (list, str):
    """
    Create a pairing for next round compared to previous round. Will call fror previous matches to avoid redundancy
    """
    # TODO : make this the function for next round
    # get previous match ups
    # careful, we are only checking previous bye player, not all of them from every previous rounds

    prev_pairing, prev_bye = get_previous_pairing(t_id, t_round)
    rand_pairing(prev_pairing, prev_bye)
########################### STOPPED HERE LAST TIME ##############################
    rand_num = random.randint(0, len(prev_pairing)-1)
    if len(prev_pairing) % 2:
        while prev_pairing[rand_num] in prev_bye:
            if rand_num < (len(prev_pairing)-1):
                rand_num += 1
            else:
                rand_num -= 1
        bye_player_name = prev_pairing.pop(rand_num)
        print("bye : ",bye_player_name)
    else:
        bye_player_name = None

    # Then let's make the pairings and avoid having the same matches as before
    # we don't handle the case when a pairing already exists but it's the last pairing !
    # previous matches not identified for reversed lists : [A, B] != [B,A]
    # Error : list index out of range
    pair_2 = 0
    pairings = list()
    print(prev_pairing)
    while prev_pairing:
        while [prev_pairing[0], prev_pairing[pair_2]] in prev_pairing:
            pair_2 += 1
        pairings.append([prev_pairing.pop(0), prev_pairing.pop(pair_2)])
        print(pairings)
        pair_2 = 0
        print(prev_pairing)
    return pairings, bye_player_name


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
        UPDATE player_matches 
        SET p_result = ?, p_score = ?  
        WHERE m_id = ? AND p_id = ?
        """,
        results
    )
    con.commit()

    return "Points updated"


if __name__ == "__main__":
    # db_create()
    # info_list = [
    #     ('Anthony', 'Guts'),
    #     ('Joey', 'Ryoma'),
    #     ('Mai', 'Valentine'),
    #     ("Ryo", "Saeba"),
    #     ("Ranni", "Zewich"),
    #     ("Neils", "Bohred")
    # ]
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
    # print("Players id table = ", id_list)
    # tourney_id = create_tourney("classic", "monday_tourney")
    # print("tourney id = ", tourney_id)
    # print(pairing_process(tourney_id, 1, id_list))

    # print( get_tourneys_list())

    # print(table_pairing(pairing_id[0]))
    # kivy table needs a tuple with all the row data : player1, player2...
    # print(pairing_process(1))
    # roco = "" \
    #        "SELECT * " \
    #        "FROM matches"
    # print(cur.execute(roco).fetchall())
    print(get_previous_pairing(1, 1))
    # results = [(1, 2, 1, 4, 7),
    #            (2, 0, 1, 5, 1),
    #            (1, 1, 1, 2, 6)]
    # enter_results(results)


