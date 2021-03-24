from copy import deepcopy
import numpy as np


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
    players = fix_ages(players, 20)
    numeric_keys = get_numeric_keys(players, unwanted_columns)
    numeric_players = map_to_only_numeric(players, numeric_keys)
    numeric_vectors = np.array(numeric_players)
    numeric_vectors = normalize_vectors(numeric_vectors)
    return numeric_vectors