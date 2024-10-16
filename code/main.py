import lc
import cc
import utils
import common
import webpage


def retrieve_data(tournament, path, token, download):
    if download:
        if tournament['website'] == 'lc':
            lc.download_data(tournament['tournament'], path, token)
        elif tournament['website'] == 'cc':
            cc.download_data(tournament['tournament'], path, token)
    return utils.read_data(tournament, path)


def update(tournament, path, token, download):
    data = retrieve_data(tournament, path, token, download)
    if tournament['tournament'] != 'scc' and tournament['tournament'] != 'bcc':
        usernames = utils.read_nicknames(path + f'in/{tournament['website']}/{tournament['website']}_usernames.csv')
        players, participation = common.analyze_winners(data, usernames, tournament)
        for n in [3, 5, 8]:
            common.create_top_json(tournament, players, n, path)
        common.create_freq_json(tournament, players, 650, path)
        if tournament['tournament'] != 'tt':
            common.create_part_json(tournament, participation, path)
            if tournament['website'] == 'lc':
                lc.create_best_json(tournament['tournament'], players, 40, path)
            else:
                cc.create_best_json(tournament['tournament'], players, 40, path)
        else:
            cc.create_part_json(participation, path)
            cc.calc_best(players, path)
        common.make_crosstable([tournament['games'] for tournament in data], usernames, next(iter(players)),
                               tournament,55, path, '')
        webpage.make_webpages(path, tournament, len(data), int(data[0]['info']['startsAt'][:4]))
        if tournament['tournament'] == 'tt' or tournament['tournament'] == 'bb':
            prefix = 'SCC' if tournament['tournament'] == 'tt' else 'BCC'
            data += utils.read_data({'website': 'cc', 'tournament': prefix}, path)
            common.make_crosstable([tournament['games'] for tournament in data], usernames, next(iter(players)),
                                   tournament, 60, path, f'{prefix}')
    return 0


def main(path, token, download):
    websites = ['cc', 'lc']
    tournaments = {'lc': ['bta', 'lta', '960'], 'cc': ['bcc', 'scc', 'bb', 'tt']}
    for website in websites:
        for tournament in tournaments[website]:
            update({'website': website, 'tournament': tournament}, path, token[website], download)


if __name__ == '__main__':
    main('../', {'lc': '', 'cc': ''}, download=True)
