import numpy as np
from sklearn.cluster import KMeans
import json


def fix_ages(player_data, default_age):
    for player in player_data:
        if player['age'] == 0:
            player['age'] = default_age*1.0


def convert_to_per_game(player_data, per_game_columns):
    for player in player_data:
        games = player['g']
        for col in per_game_columns:
            if games != 0:
                player[col] = player[col]/(games*1.0)


def get_numeric_keys(player_data, unwanted_columns):
    first_row = player_data[0]
    numeric_keys = []
    for key, value in first_row.items():
        if type(value) in [float, int]:
            if not key in unwanted_columns:
                numeric_keys.append(key)
    numeric_keys.sort()
    #print(numeric_keys)
    return numeric_keys


def only_numeric(row, numeric_keys):
    new_row = []
    for key in numeric_keys:
        new_row.append(row[key])
    return new_row


def map_to_only_numeric(player_data, numeric_keys):
    return [ only_numeric(row, numeric_keys) for row in player_data ]


def map_to_names_and_positions(player_data):
    return [ (row['player'], row['fantasy_pos']) for row in player_data ]


def normalize_column(vectors, index):
    values = vectors[:,index]
    minimum = np.min(values)
    maximum = np.max(values)
    span = maximum - minimum
    if span == 0:
        return 0
    else:
        new_values = (values - minimum) / span
        return new_values


def normalize_vectors(vectors):
    for i in range(0, len(vectors[0])):
        vectors[:,i] = normalize_column(vectors, i)


default_unwanted_columns = [
    'fantasy_points',
    'fantasy_rank_overall',
    'fantasy_rank_pos',
    'draftkings_points',
    'vbd',
    'fantasy_points_ppr',
    'fanduel_points',
    'gs',
    'g',
    'age',
    'rush_yds_per_att',
    'rec_yds_per_rec',
]

default_per_game_columns = [
    'pass_att',
    'pass_cmp',
    'pass_int',
    'pass_td',
    'pass_yds',
    'rec',
    'rec_td',
    'rec_yds',
    'rush_att',
    'rush_td',
    'rush_yds',
    'targets'
]


def cluster_players(players, k=30, unwanted_columns=default_unwanted_columns, per_game_columns=default_per_game_columns):
    # setup data for kmeans
    convert_to_per_game(players, per_game_columns)
    numeric_keys = get_numeric_keys(players, unwanted_columns)
    numeric_players = map_to_only_numeric(players, numeric_keys)
    player_names_and_positions = map_to_names_and_positions(players)
    numeric_vectors = np.array(numeric_players)
    normalize_vectors(numeric_vectors)

    # setup and run sklearn kmeans algorithm
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(numeric_vectors)
    labels = kmeans.labels_

    # create list of groups from annotated players list
    groups = []
    for i in range(k):
        current_group = []
        for j in range(len(players)):
            if labels[j] == i:
                current_group.append(players[j])
                #print(player_names_and_positions[j])
        groups.append(current_group)
    return groups


def print_cluster_groups(groups, verbose=False):
    index = 0
    for group in groups:
        if verbose:
            print("\n\n"+"#"*20)
        print("\ngroup %d:" % index)
        for player in group:
            if verbose:
                print(player)
            else:
                print(player['player']+", "+player['fantasy_pos'])
        index += 1

def load_data(filename="football_reference_2020.json", default_age=20):
    fi = open(filename, "r")
    contents = fi.read()
    fi.close()
    data = json.loads(contents)["players"]
    fix_ages(data, default_age)
    return data

def filter_by_position(player_list, position):
    filtered = [ player for player in player_list if player['fantasy_pos'] == position.upper() ]
    return filtered

if __name__ == "__main__":
    # command line args for position and num_clusters
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-p')
    parser.add_argument('-n')
    parser.add_argument('-i',nargs="+")

    args = parser.parse_args()
    num_clusters = 40
    position = ""
    custom_columns = False
    if args.p:
        position = args.p.upper()
    if args.n:
        num_clusters = int(args.n)
    if args.i:
        new_unwanted_columns = [ col for col in default_unwanted_columns if col not in args.i ]
        custom_columns = True

    # read player data that will be clustered
    data = load_data()

    if position:
        data = filter_by_position(data, position)
    if custom_columns:
        groups = cluster_players(data, k=num_clusters, unwanted_columns=new_unwanted_columns)
    else:
        groups = cluster_players(data, k=num_clusters)

    print_cluster_groups(groups)
