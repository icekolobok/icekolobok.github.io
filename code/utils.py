import os
import json
import csv


def dump_json(data_json, path):
    with open(path, 'w') as json_file:
        json.dump(data_json, json_file, indent=1)
    return 0


def read_data(tournament, folder):
    path = folder + f"in/{tournament['website']}/{tournament['tournament']}"
    files_list = sorted(os.listdir(f"{path}/info/"))
    data = []
    for file_name in files_list:
        dp = {tp: json.load(open(f"{path}/{tp}/{file_name}")) for tp in ['info', 'results', 'games']}
        data.append(dp)
    return data


def read_nicknames(path):
    with open(path, encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        nick_dick = {name[0]: name[1] for name in csv_reader}
    return nick_dick
