# project structure
# KIVYMD app to make simple tourneys
# Start with simple random pairing + keep track of previous pairing for next round
# Simple database to keep track of informations and extract results in Excel ?
# Implement app in store
# Then :
# swiss round system but make it scalable for more
# visualisation for tournaments, pairing, points
# Class system for tourneys to make it customisable later

import sqlite3, datetime
import pairing as pr

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


def enroll_players(p: list) -> str:
    # check the list for format
    # check for player already existing ?
    # error messages if needed

    cur.execute(
        """INSERT INTO  players(p_name, p_surname) VALUES (?, ?)""",
        p
    )
    con.commit()
    # """SELECT p_id FROM players WHERE p_name = ? AND p_surname = ?"""
    new_player_id = cur.execute("""SELECT MAX(p_id) FROM players""")
    p_id = new_player_id.fetchall()[0][0]
    return p_id


def create_tourney(t_type: str, t_name: str, t_date: str) -> int:
    """
    initialise tournament and return the ID of the generated tournament
    """
    # today = datetime.datetime.now().strftime("%d-%m-%Y")
    params = (t_type, t_date, t_name,)
    command = """INSERT INTO tourneys(t_type, t_date, t_name) VALUES (?, ?, ?)"""
    try:
        cur.execute(command, params)
        con.commit()
    except sqlite3.IntegrityError:
        return "This tournament can't be created"

    query = """SELECT MAX(t_id) FROM tourneys"""
    id_from_new_entry = cur.execute(query).fetchall()[0][0]
    print(id_from_new_entry)
    return id_from_new_entry


def get_tourneys_list(t_id=None, t_date=None, t_name=None):
    """ Returns the list of tournaments and their details"""
    if not any((t_id, t_date, t_name)):
        tournament_list = cur.execute("""SELECT * from tourneys""")

    elif t_id:
        try:
            tournament_list = cur.execute(
                """SELECT * from tourneys WHERE (t_id=?)""",
                (t_id,)
            )
        except:
            return print("there has been a problem")


    elif t_name and t_date:
        tournament_list = cur.execute(
            """SELECT * from tourneys WHERE (t_date=? AND t_name=?)""",
            (t_date, t_name)
            )

    elif t_name:
        tournament_list = cur.execute(
            """SELECT * from tourneys WHERE INSTR(t_name, ?)""",
            (t_name,)
            )

    elif t_date:
        tournament_list = cur.execute(
            """SELECT * from tourneys WHERE (t_date=?)""",
            (t_date,)
            )


    return tournament_list.fetchall()


def get_players_id(infos: list) -> list:
    """
    takes name and/or surname and returns the players reference in the data base in format:
    [(player_id, player_name, player_surname)]
    """
    if infos[0] and infos[1]:
        names = cur.execute(
            """SELECT * FROM players WHERE (p_name =? AND p_surname= ?)""",
            infos)
    elif infos[0] and not infos[1]:
        names = cur.execute(
            """SELECT * FROM players WHERE INSTR(p_name , ?)""",
            (infos[0],)
        )
    elif not infos[0] and infos[1]:
        names = cur.execute(
            """SELECT * FROM players WHERE INSTR(p_surname , ?)""",
            (infos[1],)
        )

    return names.fetchall()


def get_players_from_id(infos: list) -> list:
    """
    takes an id and returns the players reference in the data base in format:
    [(player_id, player_name, player_surname)]
    """
    players = cur.execute("""SELECT * FROM players WHERE (p_id = ?)""", infos)
    return players.fetchall()


def read_players() -> list:
    """ get all registered players informations """

    call = cur.execute("""SELECT * FROM players""")
    return call.fetchall()


def delete_players(p_ids: list) -> str:
    """delete players based on list of ids"""

    call = """DELETE FROM players WHERE p_id = ?"""
    cur.executemany(call,p_ids)
    con.commit()
    return (p_ids)


def delete_tourney(t_ids: list) -> str:
    """delete players based on list of ids"""

    call = """DELETE FROM tourneys WHERE t_id = ?"""
    cur.executemany(call, t_ids)
    con.commit()
    return (t_ids)


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
    db_create()
    # info_list = [
    #     ('Anthony', 'Guts'),
    #     ('Joey', 'Ryoma'),
    #     ('Mai', 'Valentine'),
    #     ("Ryo", "Saeba"),
    #     ("Ranni", "Zewich"),
    #     ("Neils", "Bohred")
    # ]
    info_list = [
        ('Anthony', 'Guts'),
        ('Joey', 'Ryoma'),
        ('Mai', 'Valentine'),
        ("Ryo", "Saeba"),
        ("Ranni", "Zewich"),
        ("Neils", "Bohred"),
        ("Jensen", "Kimmit")
    ]
    enroll_players(info_list)
    play_list = read_players()
    id_list = [p[0] for p in play_list]
    # print("Players id table = ", id_list)
    tourney_id = create_tourney("classic", "monday_tourney")
    print("tourney id = ", tourney_id)
    print("pairing process : ", pr.pairing_process(tourney_id, 1, id_list))

    print("get tourney list : ", get_tourneys_list())

    # kivy table needs a tuple with all the row data : player1, player2...
    next_round = pr.next_round_pairing(1, 1)

    print("next round func : ", next_round[0], next_round[1])
    print("pairing #2", pr.pairing_process(1, 2, bye_next_round=next_round[1], pairing_next_round=next_round[0]))
    # results = [(1, 2, 1, 4, 7),
    #            (2, 0, 1, 5, 1),
    #            (1, 1, 1, 2, 6)]
    # enter_results(results)