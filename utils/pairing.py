import random, sqlite3, itertools
con = sqlite3.connect("tourney_db.db")
cur = con.cursor()


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
    Take the matches from matches table and feeds the player_matches table with the matches and IDs
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


def pairing_process(t_id: int, t_round: int, players: list = None, bye_next_round: int = None, pairing_next_round: list = None) -> (list, list):
    """
    Main process calling all pairing function in order
    """

    print("entries :", pairing_next_round, bye_next_round)

    if players:
        pairing, bye_player = rand_pairing(players)
    else:
        pairing, bye_player = pairing_next_round, bye_next_round

    round_matches = create_match(pairing, t_id, t_round, bye_player)
    print("test entries : ", pairing, bye_player)
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
    print("previous pairings to id prev bye : ", prev_pairings)
    prev_bye_player = next(filter(lambda x: len(x) == 1, prev_pairings))[0]
    print("Prev_bye_player in get previous pairing : ", prev_bye_player)

    return prev_pairings, prev_bye_player


def get_new_round_pairing(prev_pairs: list, p_ids: list) -> list:
    """Takes previous pairings and list of ids to return new unique match ups"""
    prev_pairs_list = [set(x) for x in prev_pairs]
    all_pairs = itertools.combinations(p_ids, 2)
    all_pairs_list = [set(x) for x in all_pairs]
    possible_pairings = []

    for x in range(len(all_pairs_list)):
        curr = all_pairs_list[x]
        if curr not in prev_pairs_list:
            possible_pairings.append(list(curr))

    counter = []
    new_pairing = []

    for x in possible_pairings:
        if x[0] not in counter and x[1] not in counter:
            new_pairing.append(x)
            counter.append(x[0])
            counter.append(x[1])

    return new_pairing


def next_round_pairing(t_id: int, t_round: int) -> (list, str):
    """
    Create a pairing for next round compared to previous round. Will call for previous matches to avoid redundancy
    """
    # TODO : make this the function for next round
    # get previous match ups
    # careful, we are only checking previous bye player, not all of them from every previous rounds

    prev_pairing, prev_bye = get_previous_pairing(t_id, t_round)
    # get back simple player id list
    players_list = [p for tup in prev_pairing for p in tup]

    while players_list[-1] == prev_bye:
        random.shuffle(players_list)

    new_bye_player = players_list.pop()
    new_pairing = get_new_round_pairing(prev_pairing, players_list)

    # create new pairing that checks for previous pairs not to exist
    # ToDo add the matches and player matches in the database - check if existing funcitons are ok / adaptable

    return new_pairing, new_bye_player