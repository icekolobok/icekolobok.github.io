import utils
import json
import math


class Crosstable:
    def __init__(self):
        self.players = []
        self.results = {}

    def initialize_with_players(self, players):
        self.players = players
        self.results = {}
        for player1 in players:
            self.results[player1] = {}
            for player2 in players:
                self.results[player1][player2] = 0

    def add_result(self, player1, player2, result):
        if player1 not in self.players:
            self.players.append(player1)
            self.results[player1] = {}
        if player2 not in self.players:
            self.players.append(player2)
            self.results[player2] = {}
        if result == 0:
            r1 = 0.0
            r2 = 1.0
        elif result == 1:
            r1 = 1.0
            r2 = 0.0
        elif result == 2:
            r1 = 0.5
            r2 = 0.5
        else:
            r1 = 1
            r2 = 1
        self.results[player1][player2] = self.results[player1].get(player2, 0) + r1
        self.results[player2][player1] = self.results[player2].get(player1, 0) + r2


def analyze_winners(data, usernames, t):
    # Use the largest player list length we’ve *seen* across events to size the rank histogram.
    # If info['nbPlayers'] exists it’s fine, but duplicated/old scrapes can lie.
    def _safe_nb_players(ev):
        try:
            return int(ev['info'].get('nbPlayers', 0))
        except Exception:
            return 0
    max_rank = max([_safe_nb_players(ev) for ev in data] + [0]) or 1

    players = {}        # username -> {'results': [..], 'participation': int, 'score': [..]}
    participation = []  # per-event summary you already record

    for tournament in data:
        # 1) De-duplicate entries per event by canonical username, keep the best (lowest) rank if duplicates.
        per_event = {}
        for rec in tournament['results']:
            uname_raw = rec.get('username', '')
            uname = usernames.get(uname_raw, uname_raw)  # your nicknames mapping
            old = per_event.get(uname)
            if old is None:
                per_event[uname] = rec
            else:
                try:
                    r_old = old.get('rank', 10**9)
                    r_new = rec.get('rank', 10**9)
                    if isinstance(r_new, int) and isinstance(r_old, int) and r_new < r_old:
                        per_event[uname] = rec
                except Exception:
                    pass

        # 2) Aggregate once per player per event
        tdict = {}
        for uname, rec in per_event.items():
            if uname not in players:
                players[uname] = {'results': [0] * max_rank, 'participation': 0, 'score': []}

            # Only stamp a finishing position for TT when tie_break present (your prior rule)
            if t['tournament'] != 'tt' or rec.get('tie_break', 0) > 0:
                r = rec.get('rank')
                if isinstance(r, int) and 1 <= r <= max_rank:
                    players[uname]['results'][r - 1] += 1

            players[uname]['participation'] += 1
            players[uname]['score'].append({
                'date': tournament['info'].get('startsAt'),
                'id': tournament['info'].get('id'),
                'points': rec.get('score'),
                'rating': rec.get('rating'),
                'rank': rec.get('rank'),
                'sheet': rec['sheet']['scores'] if t['website'] == 'lc' else f"{rec.get('wins',0)}w{rec.get('draws',0)}d{rec.get('byes',0)}b",
                'performance': rec.get('performance', -1) if t['website'] == 'lc' else rec.get('tie_break', 0),
            })

            player_title = rec.get('title') or 'Untitled'
            tdict[player_title] = tdict.get(player_title, 0) + 1

        # Keep your per-event summary; use info['nbPlayers'] if you trust it.
        participation.append({
            'date': tournament['info'].get('startsAt'),
            'name': tournament['info'].get('fullName'),
            'players': tournament['info'].get('nbPlayers'),  # leave as-is if you prefer
            'unique_players': len(players),                   # cumulative unique across dataset
            'titles': tdict
        })

    sorted_ranks = dict(sorted(players.items(), key=lambda item: tuple(item[1]['results']), reverse=True))
    return sorted_ranks, participation



def create_top_json(tournament, players, n, path):
    labels = ['Gold', 'Silver', 'Bronze', 'Fourth', 'Fifth', 'Sixth', 'Seventh', 'Eighth', 'Ninth', 'Tenth']
    bg = [{'R': 212, 'G': 175, 'B': 55, 'A': 0.5}, {'R': 172, 'G': 172, 'B': 172, 'A': 0.5},
          {'R': 205, 'G': 127, 'B': 50, 'A': 0.5}, {'R': 31, 'G': 117, 'B': 254, 'A': 0.2},
          {'R': 0, 'G': 173, 'B': 131, 'A': 0.2}, {'R': 255, 'G': 0, 'B': 0, 'A': 0.1},
          {'R': 191, 'G': 0, 'B': 255, 'A': 0.2}, {'R': 136, 'G': 176, 'B': 75, 'A': 0.2}]
    bd = [{'R': 198, 'G': 147, 'B': 10, 'A': 1.0}, {'R': 132, 'G': 132, 'B': 130, 'A': 1.0},
          {'R': 165, 'G': 113, 'B': 100, 'A': 1.0}, {'R': 0, 'G': 24, 'B': 168, 'A': 0.5},
          {'R': 1, 'G': 163, 'B': 104, 'A': 0.5}, {'R': 255, 'G': 0, 'B': 0, 'A': 0.5},
          {'R': 128, 'G': 0, 'B': 128, 'A': 0.5}, {'R': 0, 'G': 148, 'B': 115, 'A': 0.5}]
    ranks_cut = {key: value for key, value in players.items() if sum(value['results'][0:n]) > 0}
    data_json = {'labels': list(ranks_cut.keys()), 'datasets': []}
    for i in range(n):
        sub_bar_data = []
        for key, value in ranks_cut.items():
            sub_bar_data.append(int(value['results'][i]))
        bar = {'label': labels[i], 'data': sub_bar_data,
               'backgroundColor': f'rgba({bg[i]['R']}, {bg[i]['G']}, {bg[i]['B']}, {bg[i]['A']})',
               'borderColor': f'rgba({bd[i]['R']}, {bd[i]['G']}, {bd[i]['B']}, {bd[i]['A']})',
               'borderWidth': 1
               }
        data_json['datasets'].append(bar)
    utils.dump_json(data_json, path + f'{tournament['website']}/{tournament['tournament']}/data/data{n}.json')
    return 0


def create_freq_json(tournament, players, n, path):
    players = dict(sorted(players.items(), key=lambda item: item[1]['participation'], reverse=True)[:n])
    f_json = {
        'labels': list(players.keys()),
        'datasets': [
            {
                'label': "Tournaments",
                'data': [value['participation'] for value in players.values()],
                'backgroundColor': "rgba(0, 175, 55, 0.5)",
                'borderColor': "rgb(93, 153, 72)",
                'borderWidth': 1
            }
        ]
    }
    utils.dump_json(f_json, path + f'{tournament['website']}/{tournament['tournament']}/data/freq.json')
    return 0


def sorted_list(table, player0):
    """
    Return an ordering of players by a greedy 'most-connected next' rule.
    Robust to:
      - empty table
      - player0 not present in the table
      - player0 having no edges (empty row)
    """
    if not table:
        return []

    # If the requested seed isn't present, start from the most-connected player.
    if player0 not in table:
        player0 = max(table.keys(), key=lambda k: sum(table[k].values()) if isinstance(table[k], dict) else 0)

    players = [player0]

    # Build the initial frontier, excluding already-picked players.
    row0 = table.get(player0, {}) or {}
    cum_dict = {k: v for k, v in row0.items() if k not in players}

    # If there are other players but the seed row is empty, seed zeros for them.
    if not cum_dict and len(table) > 1:
        for k in table.keys():
            if k not in players:
                cum_dict[k] = 0

    while len(players) < len(table):
        # If frontier is empty (disconnected component), pick any remaining player.
        if not cum_dict:
            remaining = [k for k in table.keys() if k not in players]
            if not remaining:
                break
            next_p = remaining[0]
        else:
            next_p = max(cum_dict, key=cum_dict.get)

        players.append(next_p)
        # Remove from frontier
        if next_p in cum_dict:
            cum_dict.pop(next_p, None)

        # Expand frontier with the new row
        row = table.get(next_p, {}) or {}
        for k, v in row.items():
            if k not in players:
                cum_dict[k] = cum_dict.get(k, 0) + v

        # If still empty but there are more players left, seed zeros for them.
        if not cum_dict and len(players) < len(table):
            for k in table.keys():
                if k not in players:
                    cum_dict[k] = 0

    return players


def build_crosstable(data_games, usernames, player0, website):
    games = [game for tournament in data_games for game in tournament]
    count_table = Crosstable()
    games_s = []
    winner_result_map = {'black': 0, 'white': 1}
    for game in games:
        if website == 'lc':
            white = usernames.get(game['players']['white']['user']['name'], game['players']['white']['user']['name'])
            black = usernames.get(game['players']['black']['user']['name'], game['players']['black']['user']['name'])
            if game['status'] == 'draw' or '1/2-1/2' in game['pgn']:
                result = 2
            else:
                result = winner_result_map.get(game['winner'])
        else:
            white = usernames.get(game['w'], game['w'])
            black = usernames.get(game['b'], game['b'])
            result = game['r']
        games_s.append({'white': white, 'black': black, 'result': result})
        count_table.add_result(white, black, 3)
    vals = [
        count_table.results[p][o]
        for p in count_table.results
        for o in count_table.results[p]
    ]
    max_games = max(vals) if vals else 0
    if player0 not in count_table.results and count_table.results:
        player0 = next(iter(count_table.results))  # or pick most-connected as above
    sorted_players = sorted_list(count_table.results, player0)
    table = Crosstable()
    table.initialize_with_players(sorted_players)
    for game in games_s:
        table.add_result(game['white'], game['black'], game['result'])
    return table.results, max_games


def crop_key(key, method):
    unique_names = {'Jose Carlos Ibarra Jerez':    ['Ibarra',        'Jose Carlos Ibarra'],
                    'Alexandros Papasimakopoulos': ['Alexandros P.', 'A. Papasimakopoulos'],
                    'Rasmus Svane':                ['R. Svane',      'Rasmus Svane'],
                    'Frederik Svane':              ['F. Svane',      'Frederik Svane'],
                    'Jose Martinez Alcantara':     ['Jospem',        'Jose Martinez'],
                    'Le Tuan Minh':                ['Minh Le',       'Le Tuan Minh'],
                    'Pranav Venkatesh':            ['Pranav V',      'Pranav Venkatesh'],
                    'Harshavardhan G B':           ['Harshavardhan', 'Harshavardhan G B'],
                    'Olexandr Bortnyk':            ['O. Bortnyk',    'Olexandr Bortnyk'],
                    'Mykola Bortnyk':              ['M. Bortnyk',    'Mykola Bortnyk']
                    }
    if key in unique_names:
        key_p = unique_names[key][0] if method == 'short' else unique_names[key][1] if method == 'long' else key
    else:
        text_to_delete = [' (?)', ' (X)', ' (i)', ' (S)', ' (M)', ' (!)', ' (B)', ' (C)', ' (*)', ' (d)']
        key_p = key
        for text in text_to_delete:
            key_p = key_p.replace(text, '')
        key_p = key_p.split(' ')[-1] if method == 'short' else key_p.strip()
    return key_p


def calc_color(x, y, m):
    z = x / (x + y)
    r = 0 if z > 0.5 else 255 * (1 - 2 * z)
    g = 255 * (2 * z - 1) if z > 0.5 else 0
    b = 255 * (2 - 2 * z) if z > 0.5 else 255 * 2 * z
    # a = (x + y) / m
    a0 = 0.05
    a1 = 0.7
    a = (a0 * math.sqrt(m) - a1 + (a1 - a0) * math.sqrt(x + y)) / (math.sqrt(m) - 1)
    color = f'rgba({int(r)}, {int(g)}, {int(b)}, {a:.2f})'
    return color


def create_table_html(crosstable, m, arena_type, n, path, ext):
    symbol = {'cc': '♟︎', 'lc': '♘'}
    title = {'tt': 'Titled Tuesday', 'bb': 'Bullet Brawl',
             'lta': 'Titled Arena', 'bta': 'Blitz Titled Arena', '960': 'Chess960 Titled Arena'}
    t_ext = '' if ext == '' else f' & {ext}'
    keys = list(crosstable.keys())[:n]
    html = (f'<table border="1" style="border-collapse: collapse; text-align: center; font-size: 9px; line-height: 1.2;">\n<tr>'
            f'<th>{symbol[arena_type['website']]} {title[arena_type['tournament']]}{t_ext}</th>')
    if arena_type == 'tt' or arena_type == 'bta':
        width = 1.7
    elif ext == '':
        width = 1.69
    else:
        width = 1.55
    for key in keys:
        key_p = crop_key(key, 'short')
        html += f'<th style="width: {width}%; writing-mode: vertical-lr; transform: rotate(180deg);">{key_p}</th>'
    html += '</tr>\n'
    for key1 in keys:
        key_p = crop_key(key1, 'long')
        html += f'<tr><td style="text-align: left; white-space: nowrap;">{key_p}</td>'
        for key2 in keys:
            if key1 == key2 and crosstable[key1][key1] == 0:
                cell = '&nbsp'
                cell_style = 'background-color: black;'
            else:
                if crosstable[key1][key2] == crosstable[key2][key1] == 0:
                    cell = '-'
                    cell_style = 'background-color: lightgray;'
                else:
                    cell_f = crosstable[key1].get(key2, "")
                    cell = int(cell_f)
                    if cell < cell_f:
                        if cell > 0:
                            cell = f'{cell}½'
                        else:
                            cell = '½'
                    cell_color = calc_color(crosstable[key1][key2], crosstable[key2][key1], m)
                    cell_style = f'background-color: {cell_color};'
            html += f'<td style="{cell_style}">{cell}</td>'
        html += '</tr>\n'
    html += '</table>'
    with open(path + f'{arena_type['website']}/{arena_type['tournament']}/data/crosstable{ext}.html', 'w', encoding='utf-8') as f:
        f.write(html)
    return 0


def make_crosstable(data_games, nicknames, player0, tournament, n, path, ext):
    if tournament['tournament'] == 'tt':
        filename = 'scc_playoff-1613698.json'
        data_games.append(json.load(open(path + f'in/{tournament['website']}/{tournament['tournament']}/games/{filename}')))
    crosstable, max_games = build_crosstable(data_games, nicknames, player0, tournament['website'])
    create_table_html(crosstable, max_games, tournament, n, path, ext)
    return 0


def add_line(participation):
    line = {'label': 'Unique Players',
            'data': [{'x': tournament['date'],
                      'y': tournament['unique_players']} for tournament in participation],
            'borderColor': f'rgba(0, 0, 0, 1)',
            'type': 'line',
            'borderWidth': 3,
            'pointRadius': 0,
            'cubicInterpolationMode': 'monotone',
            'fill': False,
            'yAxisID': 'y2'
            }
    return line


def create_part_json(arena_type, participation, folder):
    # titles = list({key for tournament in participation for key in tournament['titles']})
    titles = ['GM', 'IM', 'WGM', 'FM', 'WIM', 'CM', 'WFM', 'WCM', 'NM', 'WNM', 'Untitled']
    bg = {'GM': {'R':   0, 'G':  35, 'B': 102, 'A': 0.7}, 'WGM': {'R': 187, 'G':  38, 'B':  73, 'A': 0.7},
          'IM': {'R':  31, 'G': 117, 'B': 254, 'A': 0.7}, 'WIM': {'R': 237, 'G':  10, 'B':  63, 'A': 0.7},
          'FM': {'R':  83, 'G': 176, 'B': 174, 'A': 0.7}, 'WFM': {'R': 217, 'G':  79, 'B': 112, 'A': 0.7},
          'CM': {'R':   0, 'G': 173, 'B': 131, 'A': 0.7}, 'WCM': {'R': 255, 'G': 111, 'B':  97, 'A': 0.7},
          'NM': {'R': 136, 'G': 176, 'B':  75, 'A': 0.7}, 'WNM': {'R': 240, 'G': 192, 'B':  90, 'A': 0.7},
          'LM': {'R': 255, 'G': 255, 'B': 255, 'A': 0.7}, 'Untitled': {'R': 147, 'G': 149, 'B': 151, 'A': 0.7}}
    bd = {'GM': {'R':   0, 'G':  35, 'B': 102, 'A': 1.0}, 'WGM': {'R': 187, 'G':  38, 'B':  73, 'A': 1.0},
          'IM': {'R':  31, 'G': 117, 'B': 254, 'A': 1.0}, 'WIM': {'R': 237, 'G':  10, 'B':  63, 'A': 1.0},
          'FM': {'R':  83, 'G': 176, 'B': 174, 'A': 1.0}, 'WFM': {'R': 217, 'G':  79, 'B': 112, 'A': 1.0},
          'CM': {'R':   0, 'G': 173, 'B': 131, 'A': 1.0}, 'WCM': {'R': 255, 'G': 111, 'B':  97, 'A': 1.0},
          'NM': {'R': 136, 'G': 176, 'B':  75, 'A': 1.0}, 'WNM': {'R': 240, 'G': 192, 'B':  90, 'A': 1.0},
          'LM': {'R':   0, 'G':   0, 'B': 255, 'A': 1.0}, 'Untitled': {'R': 147, 'G': 149, 'B': 151, 'A': 1.0}}

    p_json = {'labels': [tournament['date'] for tournament in participation], 'datasets': []}
    for title in titles:
        bar = {'label': title,
               'data': [{'x': tournament['date'],
                         'y': tournament['titles'].get(title, 0)} for tournament in participation],
               'backgroundColor': f'rgba({bg[title]['R']}, {bg[title]['G']}, {bg[title]['B']}, {bg[title]['A']})',
               'borderColor': f'rgba({bd[title]['R']}, {bd[title]['G']}, {bd[title]['B']}, {bd[title]['A']})',
               'borderWidth': 1,
               'yAxisID': 'y1'
               }
        p_json['datasets'].append(bar)
    line = add_line(participation)
    p_json['datasets'].append(line)
    utils.dump_json(p_json, folder + f'{arena_type['website']}/{arena_type['tournament']}/data/participation.json')
    return 0
