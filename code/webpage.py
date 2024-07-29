from datetime import datetime


def name(tournament):
    tournament_name = {'tt': 'Titled Tuesday',
                       'bb': 'Bullet Brawl',
                       'lta': 'Titled Arena',
                       'bta': 'Blitz Titled Arena',
                       '960': 'Chess960 Titled Arena',
                       'lc': 'Lichess.org',
                       'cc': 'Chess.com',
                       }
    return tournament_name[tournament]


def make_header(path, tournament, page_type, n_ev, year):
    with open(path + 'in/templates/header.html') as file:
        header = file.read()
    page_name = {'top3': 'Winners and Statistics',
                 'top5': 'Winners',
                 'top8': 'Winners',
                 'h2h':  'Direct Encounter',
                 'best': 'Highest Scores',
                 'p':    'Participation Statistics',
                 'freq': 'Statistics'}
    title = f"{name(tournament['tournament'])} {page_name[page_type]}"
    header += f'\n <title>{title}</title>\n'
    header += f' <meta property="og:title" content="{title}"/>\n'
    header += f' <meta property="og:description" content="{name(tournament['website'])} {title}"/>\n'
    if (tournament['tournament'] != 'tt' or page_type != 'best') and page_type != 'h2h':
        header += ' <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>\n'
    scripts = ['chartjs-adapter-date-fns', 'chartjs-plugin-datalabels', 'chart.min.js', 'chartjs-plugin-annotation']
    if page_type == 'p':
        for script in scripts:
            header += f' <script src="https://cdn.jsdelivr.net/npm/{script}"></script>\n'
    elif page_type == 'h2h':
        header += ' <script src="../scripts/scriptt.js"></script>\n'
    elif page_type == 'best' and tournament['tournament'] == 'tt':
        header += ' <script src="../scripts/scriptb.js"></script>\n'
    if tournament['tournament'] == 'tt' and page_type == 'top3':
        header += ('<script type="application/ld+json">\n'
                   '{"@context": "https://www.titled-tuesday.com",\n'
                   '"@type" : "WebSite",\n'
                   '"name" : "Titled Tuesday, Bullet Brawl and Titled Arenas Winners and Statistics",\n'
                   '"url" : "https://www.titled-tuesday.com/",\n'
                   '"alternateName": "Chess Statistics"}\n'
                   '</script>\n')
    header += '</head>\n'
    header += '<body>\n'
    header += f' <h1 class="chart-title">{name(tournament['website'])} {title}, {n_ev} events since {year}</h1>\n'
    return header


def generate_table(tournament, page_type):
    table = ' <table class="header-table">\n'
    table += '  <tr>\n'
    sites = {'cc': ['tt', 'bb'], 'lc': ['lta', 'bta', '960']}
    for site, tournaments in sites.items():
        for t in tournaments:
            if tournament['tournament'] != t:
                if tournament['website'] == site:
                    prefix = t
                else:
                    prefix = f'../{site}/{t}'
                table += f'   <td><a href="../../{prefix}/html/{page_type}.html" class="chart-url"><b>{name(t)}</b></a></td>\n'
            else:
                table += f'   <td class="ss"><b>{name(t)}</b></td>\n'
    table += '  </tr>\n'
    table += ' </table>\n'
    table += '    <table class="top-table">\n'
    table += '        <tr>\n'
    names = {'top3': 'Top-3', 'top5': 'Top-5', 'top8': 'Top-8', 'h2h': 'Head-to-Head Crosstable',
             'best': 'Highest Scores', 'p': 'Participation', 'freq': 'Most Tournaments Played'}
    for top in ['top3', 'top5', 'top8']:
        if page_type != top:
            table += f'   <td><a href="{top}.html" class="chart-url">{names[top]}</a></td>'
        else:
            table += f'   <td>{names[top]}</td>\n'
    table += '  </tr>\n'
    table += ' </table>\n'
    table += ' <table class="header-table">\n'
    table += '  <tr>\n'
    for tp in ['h2h', 'best', 'p', 'freq']:
        if page_type != tp:
            table += f'   <td><a href="{tp}.html" class="chart-url">{names[tp]}</a></td>'
        else:
            table += f'   <td>{names[tp]}</td>\n'
    table += '  </tr>\n'
    table += ' </table>\n'
    return table


def make_body(tournament, page_type):
    body = generate_table(tournament, page_type)
    tags = {'top3': 3, 'top5': 5, 'top8': 8, 'h2h': 't', 'best': 'b', 'p': 'p', 'freq': 'f'}
    if page_type == 'h2h' or (tournament['tournament'] == 'tt' and page_type == 'best'):
        body += ' <my-table></my-table>\n'
    else:
        tag = tags[page_type]
        body += f' <div class="chart-container{tag}"><canvas id="myChart"></canvas></div>\n'
        body += f' <script src="../scripts/script{tag}.js"></script>'
    if tournament['tournament'] == 'tt' and page_type == 'h2h':
        body += '  <a href="h2h_ext.html" target="_blank" style="font-size: 0.6em;">Include SCC Swiss Qualifiers</a>'
    if tournament['tournament'] == 'bb' and page_type == 'h2h':
        body += '  <a href="h2h_ext.html" target="_blank" style="font-size: 0.6em;">Include BCC Swiss Qualifiers</a>'
    if tournament['website'] == 'cc' and page_type in ['top3', 'top5', 'top8']:
        body += ' <div class="note">(X) - account closed, (M), (S), (B), (C), (?), (!) - have a history of account closures/inactivities/2nd chance accounts, (i) - inactive, (d) - deceased</div>\n'
        body += ' <div class="note">These marks help accumulate results from different accounts of the same player and do not imply cheating, unfair play, or rule violations. For details see Fair Play section in TT Highest Scores tab.</div>\n'
    body += f' <div class="note">Last Updated: {datetime.now().strftime("%d %B %Y at %H:%M:%S")} ET</div>\n'
    body += '</body>\n'
    body += '</html>'
    return body


def write_page(path, tournament, page_type, html_content):
    out_file = path + f'{tournament["website"]}/{tournament["tournament"]}/html/{page_type}.html'
    with open(out_file, mode='w') as file:
        file.write(html_content)
    return 0


def make_webpage(path, tournament, page_type, n_ev, year):
    html_content = make_header(path, tournament, page_type, n_ev, year) + make_body(tournament, page_type)
    write_page(path, tournament, page_type, html_content)
    return 0


def make_webpages(path, tournament, n_ev, year):
    page_types = ['top3', 'top5', 'top8', 'h2h', 'best', 'p', 'freq']
    for page_type in page_types:
        make_webpage(path, tournament, page_type, n_ev, year)
    return 0
