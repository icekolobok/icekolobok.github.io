import json
import os
import json
import utils
import requests
import common


def generate_links(arena_type, folder):
    base_url = 'https://lichess.org/api/tournament/'
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    years = ['19', '20', '21', '22', '23', '24', '25']
    links = []
    for year in years:
        for month in months:
            date = month + year
            if arena_type == '960':
                t_id = arena_type + date
            else:
                t_id = date + arena_type
            links.append(base_url + f'{t_id}')
    if arena_type == 'lta':
        # old_ids = ['GToVqkC9', 'WfvjOFkB', '9kuznL7F', 'qkdW41M2', 'dyhuymXb',
        #            '3ImmfhBr', 'yuZKAN0m', '7cFYtxgA', 'Te1RcjFI']
        with open(folder + f'in/lc/{arena_type}/old_ids.txt') as file:
            old_links = [base_url + line.strip() for line in file]
        links = old_links + links
    return links


def get(url, params, content_type, token):
    headers = {'Authorization': f'Bearer {token}', 'Accept': f'application/{content_type}'}
    response = requests.get(url=url, headers=headers, params=params, allow_redirects=True, verify=True, stream=False)
    return response


def download_data(arena_type, folder, token):
    tournament_urls = generate_links(arena_type, folder)
    params = {'page': 1}
    for url in tournament_urls:
        response = get(url, params, 'json', token)
        if response.status_code == 200:
            info = response.json()
            name = info['startsAt'].replace(':', ';') + ' ' + info['fullName']
            if 'isFinished' in info and info['isFinished']:
                path = folder + f'in/lc/{arena_type}/'
                filename = f'{name}.json'
                directories = ['info', 'results', 'games']
                if all(os.path.exists(os.path.join(path, directory, filename)) for directory in directories):
                    print(f'{name}: Already downloaded')
                else:
                    utils.dump_json(info, os.path.join(path, directories[0], filename))
                    for tp in directories[1:3]:
                        if tp == 'results':
                            params = {'nb': info['nbPlayers'], 'sheet': True}
                        else:
                            params = {'moves': True, 'pgnInJson': True, 'tags': True, 'clocks': True, 'evals': True,
                                      'accuracy': True, 'opening': True, 'division': True}
                        response = get(url + f'/{tp}', params, 'x-ndjson', token)
                        if response.status_code == 200:
                            data = response.text.strip().split('\n')
                            dicts = [json.loads(line) for line in data]
                            utils.dump_json(dicts, path + f'{tp}/' + filename)
                            print(f'{name}: {tp} downloaded')
                        else:
                            print(f'{name}: {response.status_code}')
            else:
                print(f'{name}: Arena starts in {info['secondsToStart']} seconds')
    return 0


def colormap(performances, a):
    cmap = {'Magnus Carlsen':          f'rgba(182,  12,  47, {a})',
            'Daniel Naroditsky':       f'rgba( 10,  49,  97, {a})',
            'Olexandr Bortnyk':        f'rgba(255, 215,   0, {a})',
            'Alireza Firouzja':        f'rgba( 35, 159,  64, {a})',
            'Jose Martinez Alcantara': f'rgba(  0, 104,  71, {a})',
            'Andrew Tang':             f'rgba( 95,  37,  82, {a})',
            'Nihal Sarin':             f'rgba(255, 103,  31, {a})',
            'Dmitry Andreikin':        f'rgba(  0, 171, 194, {a})',
            'Le Tuan Minh':            f'rgba(218,  37,  29, {a})',
            'Sergei Zhigalko':         f'rgba(105,  95,  52, {a})',
            'Yoseph Theolifus Taher':  f'rgba(246, 142, 146, {a})',
            'Jeffery Xiong':           f'rgba(179,  25,  66, {a})',
            'David Paravyan':          f'rgba(242, 168,   0, {a})',
            'Vladislav Artemiev':      f'rgba(  0,  50, 160, {a})',
            'Arjun Erigaisi':          f'rgba(130, 105,  44, {a})',
            'Daniil Dubov':            f'rgba(168,   0,  44, {a})',
            'Sanan Sjugirov':          f'rgba(177, 136, 131, {a})',
            'Akshat Chandra':          f'rgba(130, 117, 121, {a})',
            'Mykola Bortnyk':          f'rgba(  0,  87, 183, {a})',
            'Benjamin Bok':            f'rgba(102,  50,  85, {a})',
            'Mahammad Muradli':        f'rgba(  0, 181, 226, {a})',
            'Vugar Rasulov':           f'rgba( 80, 158,  47, {a})',
            'Volodar Murzin':          f'rgba(218,  41,  28, {a})',
            'Janak Awatramani':        f'rgba(127,   0,   0, {a})',
            'Zaven Andriasian':        f'rgba(153,  73,  59, {a})',
            'Shamsiddin Vokhidov':     f'rgba( 83, 176, 174, {a})',
            'Javokhir Sindarov':       f'rgba(136, 176,  75, {a})'}
    return [cmap.get(performance['player'], f'rgba(192, 192, 192, {a})') for performance in performances]


def create_best_json(arena_type, players, n, folder):
    performances = sorted(
        [
            {
                'player': name,
                'date': tournament['date'],
                'score': tournament['points'],
                'performance': tournament['performance'],
                'rank': tournament['rank'],
                'rating': tournament['rating'],
            }
            for name, results in players.items()
            for tournament in results['score']
        ],
        key=lambda x: (x['score'], x['performance'], -x['rank'], x['date']),
        reverse=True
    )[:n]

    b_json = {
        'labels': [performance['player'] + f' ({performance['date'].split('T')[0]}, {performance['rank']} place, rating: {performance['rating']})' for performance in performances],
        'datasets': [
            {
                'label': 'Points',
                'data': [performance['score'] for performance in performances],
                'backgroundColor': colormap(performances, 1.0),
                'borderColor': "rgb(0, 0, 0)",
                'borderWidth': 1,
                'xAxisID': 'x1'
            },
            {
                'label': 'Performance Rating',
                'data': [performance['performance'] for performance in performances],
                'backgroundColor': colormap(performances, 0.4),
                'borderColor': "rgb(0, 0, 0)",
                'borderWidth': 1,
                'xAxisID': 'x2'
            }
        ]
    }
    utils.dump_json(b_json, folder + f'lc/{arena_type}/data/best.json')
    return 0
