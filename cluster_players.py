import numpy as np
from sklearn.cluster import KMeans
import argparse
import json
from copy import deepcopy
from collections import defaultdict
import sys


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


def fix_ages(player_data, default_age):
    results = []
    for old_player in player_data:
        player = deepcopy(old_player)
        if player['age'] == 0:
            player['age'] = default_age*1.0
        results.append(player)
    return results


def convert_to_per_game(player_data, per_game_columns):
    results = []
    for old_player in player_data:
        player = deepcopy(old_player)
        games = player['g']
        for col in per_game_columns:
            if games != 0:
                player[col] = player[col]/(games*1.0)
        results.append(player)
    return results


def get_numeric_keys(player_data, unwanted_columns):
    first_row = player_data[0]
    numeric_keys = []
    for key, value in first_row.items():
        if type(value) in [float, int]:
            if not key in unwanted_columns:
                numeric_keys.append(key)
    numeric_keys.sort()
    return numeric_keys


def only_numeric(row, numeric_keys):
    new_row = []
    for key in numeric_keys:
        new_row.append(row[key])
    return new_row


def map_to_only_numeric(player_data, numeric_keys):
    return [only_numeric(row, numeric_keys) for row in player_data]


def normalize_column(vectors, index):
    values = vectors[:, index]
    minimum = np.min(values)
    maximum = np.max(values)
    span = maximum - minimum
    if span == 0:
        return 0
    else:
        new_values = (values - minimum) / span
        return new_values


def normalize_vectors(vectors):
    results = deepcopy(vectors)
    for i in range(0, len(results[0])):
        results[:, i] = normalize_column(results, i)
    return results


def prepare_vectors(player_data, unwanted_columns, per_game_columns):
    players = convert_to_per_game(player_data, per_game_columns)
    numeric_keys = get_numeric_keys(players, unwanted_columns)
    numeric_players = map_to_only_numeric(players, numeric_keys)
    numeric_vectors = np.array(numeric_players)
    numeric_vectors = normalize_vectors(numeric_vectors)
    return numeric_vectors


def get_cluster_labels(players, k=30, unwanted_columns=default_unwanted_columns, per_game_columns=default_per_game_columns):
    # setup data for kmeans
    numeric_vectors = prepare_vectors(
        players, unwanted_columns, per_game_columns)

    # setup and run sklearn kmeans algorithm
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(numeric_vectors)
    labels = kmeans.labels_
    return labels


def annotate_players_with_labels(players, labels):
    results = deepcopy(players)
    for index, player in enumerate(results):
        label = labels[index]
        player['label'] = str(label)
    return results


def group_annotated_list_by_labels(annotated_players):
    result_dict = defaultdict(list)
    for player in annotated_players:
        result_dict[player['label']].append(player)
    return result_dict


def print_grouped_list(group_dict):
    for label, players in group_dict.items():
        print("#"*20)
        print("group "+str(label)+":")
        for player in players:
            print(player['player']+", "+player['fantasy_pos'])


def load_data(filename=None):
    filename = filename or "football_reference_2020.json"
    fi = open(filename, "r")
    contents = fi.read()
    fi.close()
    data = json.loads(contents)["players"]
    return data


def filter_by_position(player_list, position):
    results = player_list
    if position:
        results = [
            player for player in results if player['fantasy_pos'] == position.upper()
        ]
    return results


def run_clusters(options):
    # read player data that will be clustered
    data = load_data(filename=options['data_filename'])
    # prepare for clustering
    filtered = filter_by_position(data, options['position'])
    filtered_and_fixed = fix_ages(filtered, 20)
    labels = get_cluster_labels(
        filtered_and_fixed, k=options['num_clusters'], unwanted_columns=options['unwanted_columns'])
    annotated = annotate_players_with_labels(filtered, labels)
    return annotated


def parse_args(args):
    parser = argparse.ArgumentParser()
    # position filter
    parser.add_argument('-p')
    # number of clusters
    parser.add_argument('-n')
    # file for json data source
    parser.add_argument('-f')
    # flag for outputting json instead of printing formatted list
    parser.add_argument('-j', action="store_const", const=True)
    # include would-be-excluded data dimensions
    parser.add_argument('-i', nargs="+")
    parsed = parser.parse_args(args)
    return parsed


def option_dict_from_args(args):
    num_clusters = 30
    position = ""
    custom_columns = False
    data_filename = None
    unwanted_columns = default_unwanted_columns
    output_json = False
    if args.p:
        position = args.p.upper()
    if args.n:
        num_clusters = int(args.n)
    if args.f:
        data_filename = args.f
    if args.j:
        output_json = True
    if args.i:
        unwanted_columns = [
            col for col in default_unwanted_columns if col not in args.i]
    else:
        unwanted_columns = default_unwanted_columns
    return {
        'num_clusters': num_clusters,
        'position': position,
        'data_filename': data_filename,
        'unwanted_columns': unwanted_columns,
        'output_json': output_json
    }


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    options = option_dict_from_args(args)
    annotated_players = run_clusters(options)
    if options['output_json']:
        print(json.dumps(annotated_players))
    else:
        grouped = group_annotated_list_by_labels(annotated_players)
        print_grouped_list(grouped)
