import os
# import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import common
import utils
import re


def _get_total_pages(soup):
    pag = soup.find("div", class_="index-pagination")
    if not pag:
        return 1
    nums = []
    for btn in pag.find_all(["button", "a"]):
        txt = (btn.get_text(strip=True) or "")
        if txt.isdigit():
            nums.append(int(txt))
    return max(nums) if nums else 1

def _first_username_from_results(soup):
    table = soup.find("table", class_=re.compile(r"tournaments-live-view-results-table"))
    if not table:
        return None
    rows = table.find_all("tr")[1:]
    if not rows:
        return None
    # Username moved to cc-user-username-component; keep a fallback
    u = rows[0].select_one('a.cc-user-username-component[href*="/member/"]')
    if u:
        return u.get_text(strip=True)
    u = rows[0].select_one(".user-tagline-username")
    if u:
        return u.get_text(strip=True)
    a_any = rows[0].find("a", href=re.compile(r"/member/"))
    return a_any.get_text(strip=True) if a_any else None

def _fetch_results_page_soup(session, base_url, page):
    """
    Try likely query patterns until the first username differs from page 1,
    to avoid re-parsing page 1 when a pattern is wrong.
    """
    sep = "&" if "?" in base_url else "?"
    candidates = [
        f"{base_url}{sep}players=100&page={page}",  # best (bigger pages if supported)
        f"{base_url}{sep}page={page}&players=100",
        f"{base_url}{sep}page={page}",
        f"{base_url}{sep}playersPage={page}",
        f"{base_url}{sep}players={page}",
    ]
    first_page_soup = session.get(base_url, timeout=20)
    first_name = _first_username_from_results(BeautifulSoup(first_page_soup.content, "html.parser"))

    for url in candidates:
        r = session.get(url, timeout=20)
        sp = BeautifulSoup(r.content, "html.parser")
        table = sp.find("table", class_=re.compile(r"tournaments-live-view-results-table"))
        if not table:
            continue
        name = _first_username_from_results(sp)
        if name and name != first_name:
            return sp
    # Fall back: return whatever we got with ?page=
    r = session.get(f"{base_url}{sep}page={page}", timeout=20)
    return BeautifulSoup(r.content, "html.parser")

def _parse_results_page(soup, tournament, start_rank):
    """Parse one standings page. Returns (list_of_players, new_rank)."""
    table = soup.find("table", class_=re.compile(r"tournaments-live-view-results-table"))
    if not table:
        return [], start_rank
    rows = table.find_all("tr")[1:]
    out, rank = [], start_rank
    for tr in rows:
        rank += 1

        # username (new + fallback)
        u = tr.select_one('a.cc-user-username-component[href*="/member/"]')
        if u:
            username = u.get_text(strip=True)
        else:
            u = tr.select_one(".user-tagline-username")
            if u:
                username = u.get_text(strip=True)
            else:
                a_any = tr.find("a", href=re.compile(r"/member/"))
                username = a_any.get_text(strip=True) if a_any else None

        # country tooltip
        cdiv = tr.select_one(".country-flags-component")
        country = cdiv.get("v-tooltip") if cdiv else None

        # rating
        rating_el = tr.select_one(".user-rating")
        rating = None
        if rating_el:
            txt = rating_el.get_text(strip=True)
            if txt != "Unrated":
                digits = re.sub(r"[^\d]", "", txt)
                rating = int(digits) if digits else None

        # title (new class)
        t_el = tr.select_one(".cc-user-title-component") or tr.select_one(".post-view-meta-title")
        title = t_el.get_text(strip=True) if t_el else None

        # score
        s_el = tr.select_one(".tournaments-live-view-total-score")
        try:
            score = float(re.sub(r"[^\d.]", "", s_el.get_text(strip=True))) if s_el else 0.0
        except Exception:
            score = 0.0

        # tie-breaks (TT only)
        tb_el = tr.select_one(".tournaments-live-view-tie-break")
        tie_break = float(tb_el.get_text(strip=True)) if (tb_el and tournament == "tt") else 0.0

        # wins/draws/byes from tooltip (be generous in parsing)
        wdb_tt = s_el.get("v-tooltip", "") if s_el else ""
        def _pick(pat):
            m = re.search(pat, wdb_tt, re.I)
            return int(m.group(1)) if m else 0
        wins  = _pick(r"(\d+)\s*wins?")
        draws = _pick(r"(\d+)\s*draws?")
        byes  = _pick(r"(\d+)\s*byes?")

        out.append({
            "rank": rank,
            "username": username,
            "country": country,
            "rating": rating,
            "title": title,
            "score": score,
            "tie_break": tie_break,
            "wins": wins,
            "draws": draws,
            "byes": byes,
        })
    return out, rank



def get_tournament_links(tournament, path):
    with open(path + f'in/cc/{tournament}/{tournament}_tournaments.txt') as file:
        links = file.read().splitlines()
    tournament_links = []
    if tournament == 'tt':
        base_url = 'https://www.chess.com/tournament/live/titled-tuesdays'
        number_of_pages = 24
        for page in range(number_of_pages):
            soup = BeautifulSoup(requests.get(base_url + '?&page=' + str(page + 1)).content, 'html.parser')
            tournament_list = soup.find('table',
                                        class_='table-component table-hover table-clickable tournaments-live-table')
            tournament_table_rows = tournament_list.find_all('tr')
            tournament_table_rows = tournament_table_rows[1:]
            for tournament_table_row in tournament_table_rows:
                tournament_link = tournament_table_row.find('a', class_='tournaments-live-name')['href']
                tournament_links.append(tournament_link)
    return tournament_links + links


def metadata(soup):
    try:
        name = soup.find('h1', class_='v5-title-label').get_text().strip()
    except:
        name = soup.find('h1', class_='cc-page-header-title cc-heading-small').get_text().strip()
    span_elements = soup.find('div', class_='tournaments-live-view-content-stats').find_all('span')
    number_of_players = int(span_elements[1].get_text(strip=True).split()[0])
    date_and_time = span_elements[2].get_text(strip=True)
    parsed_date = datetime.strptime(date_and_time, "%b %d, %Y, %I:%M %p")
    event = {
        'fullName': name,
        'nbPlayers': number_of_players,
        'startsAt': parsed_date.isoformat()
    }
    return event


def download_json(tournament, folder, token, url):
    """
    Scrape a Chess.com live tournament page and save:
      - info/<name>.json     (metadata)
      - results/<name>.json  (standings for all pages)
      - games/<name>.json    (all pairings for each round)
    Returns 0.
    """
    import re
    import os
    import requests
    from bs4 import BeautifulSoup

    # ---------- inner helpers (scoped to keep cc.py tidy) ----------
    def _session():
        s = requests.Session()
        s.headers.update({
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/124.0 Safari/537.36"),
            "Accept-Language": "en-US,en;q=0.8",
        })
        return s

    def _soup(resp):
        return BeautifulSoup(resp.content, "html.parser")

    def _first_username_from_results(soup):
        table = soup.find("table", class_=re.compile(r"tournaments-live-view-results-table"))
        if not table:
            return None
        rows = table.find_all("tr")[1:]
        if not rows:
            return None
        # New UI: anchor with cc-user-username-component; keep fallbacks
        u = rows[0].select_one('a.cc-user-username-component[href*="/member/"]')
        if u:
            return u.get_text(strip=True)
        u = rows[0].select_one(".user-tagline-username")
        if u:
            return u.get_text(strip=True)
        a_any = rows[0].find("a", href=re.compile(r"/member/"))
        return a_any.get_text(strip=True) if a_any else None

    def _is_last_results_page(soup):
        # Look for "Next Page" button inside index-pagination and see if it's disabled
        pag = soup.find("div", class_="index-pagination")
        if not pag:
            # If there is pagination nowhere, assume single page
            return True
        for btn in pag.find_all(["button", "a"]):
            label = (btn.get("aria-label") or btn.get_text("") or "").strip().lower()
            classes = btn.get("class") or []
            disabled_attr = btn.has_attr("disabled")
            if "next page" in label:
                return disabled_attr or any("cc-pagination-disabled" in c for c in classes)
        # If no explicit "Next Page" found, keep iterating until a page repeats.
        return False

    def _parse_results_page(soup, tournament, start_rank):
        """Parse one standings page. Returns (list_of_players, new_rank)."""
        table = soup.find("table", class_=re.compile(r"tournaments-live-view-results-table"))
        if not table:
            return [], start_rank
        rows = table.find_all("tr")[1:]
        out, rank = [], start_rank
        for tr in rows:
            rank += 1
            # username
            u = tr.select_one('a.cc-user-username-component[href*="/member/"]')
            if u:
                username = u.get_text(strip=True)
            else:
                u = tr.select_one(".user-tagline-username")
                if u:
                    username = u.get_text(strip=True)
                else:
                    a_any = tr.find("a", href=re.compile(r"/member/"))
                    username = a_any.get_text(strip=True) if a_any else None

            # country tooltip
            cdiv = tr.select_one(".country-flags-component")
            country = cdiv.get("v-tooltip") if cdiv else None

            # rating (may be 'Unrated' or '(xxxx)')
            rating_el = tr.select_one(".user-rating")
            rating = None
            if rating_el:
                txt = rating_el.get_text(strip=True)
                if txt != "Unrated":
                    digits = re.sub(r"[^\d]", "", txt)
                    try:
                        rating = int(digits) if digits else None
                    except Exception:
                        rating = None

            # title
            t_el = tr.select_one(".cc-user-title-component") or tr.select_one(".post-view-meta-title")
            title = t_el.get_text(strip=True) if t_el else None

            # score
            s_el = tr.select_one(".tournaments-live-view-total-score")
            if s_el:
                txt = s_el.get_text(strip=True)
                try:
                    score = float(re.sub(r"[^\d.]", "", txt))
                except Exception:
                    score = 0.0
            else:
                score = 0.0

            # tie-break (present in some formats like TT)
            tb_el = tr.select_one(".tournaments-live-view-tie-break")
            tie_break = 0.0
            if tournament == "tt" and tb_el:
                try:
                    tie_break = float(tb_el.get_text(strip=True))
                except Exception:
                    tie_break = 0.0

            # wins/draws/byes from tooltip on total-score
            wdb_tt = s_el.get("v-tooltip", "") if s_el else ""
            def _pick(pat):
                m = re.search(pat, wdb_tt, re.I)
                return int(m.group(1)) if m else 0
            wins  = _pick(r"(\d+)\s*wins?")
            draws = _pick(r"(\d+)\s*draws?")
            byes  = _pick(r"(\d+)\s*byes?")

            out.append({
                "rank": rank,
                "username": username,
                "country": country,
                "rating": rating,
                "title": title,
                "score": score,
                "tie_break": tie_break,
                "wins": wins,
                "draws": draws,
                "byes": byes,
            })
        return out, rank

    def _fetch_results_page_soup(session, base_url, page, prev_first):
        """
        Try likely query patterns until the first username differs from the previous page.
        Returns (soup, first_username) or (None, None) if no valid table found.
        """
        sep = "&" if "?" in base_url else "?"
        candidates = [
            f"{base_url}{sep}players=100&page={page}",  # preferred when supported
            f"{base_url}{sep}page={page}&players=100",
            f"{base_url}{sep}page={page}",
            f"{base_url}{sep}playersPage={page}",
            f"{base_url}{sep}players={page}",
        ]
        for u in candidates:
            r = session.get(u, timeout=20)
            sp = _soup(r)
            table = sp.find("table", class_=re.compile(r"tournaments-live-view-results-table"))
            if not table:
                continue
            first_name = _first_username_from_results(sp)
            # accept when first username changes from prev page
            if first_name and first_name != prev_first:
                return sp, first_name
        # As a last resort, return the ?page= variant even if it repeats
        r = session.get(f"{base_url}{sep}page={page}", timeout=20)
        sp = _soup(r)
        return sp, _first_username_from_results(sp)

    def _pairings_table_to_games(soup):
        """Extract games from a pairings page soup."""
        table = soup.find("table", class_=re.compile(r"tournaments-live-view-pairings-table"))
        if not table:
            return []
        rows = table.find_all("tr")[1:]
        games = []
        for tr in rows:
            users = tr.find_all("div", class_="tournaments-live-view-pairings-user")
            if len(users) < 2:
                continue
            txt = tr.get_text(" ", strip=True)
            if "1 - 0" in txt:
                r = 1
            elif "0 - 1" in txt:
                r = 0
            elif "½ - ½" in txt or "1/2 - 1/2" in txt:
                r = 2
            else:
                r = 3  # unknown / not finished

            def _nick(u):
                a = u.find("a", class_="tournaments-live-view-player-avatar")
                return a.get("title", "") if a else ""

            games.append({"w": _nick(users[0]), "b": _nick(users[1]), "r": r})
        return games

    def _is_last_pairings_page(soup):
        pag = soup.find("div", class_="index-pagination")
        if not pag:
            return True
        for btn in pag.find_all(["button", "a"]):
            label = (btn.get("aria-label") or btn.get_text("") or "").strip().lower()
            classes = btn.get("class") or []
            disabled_attr = btn.has_attr("disabled")
            if "next page" in label:
                return disabled_attr or any("cc-pagination-disabled" in c for c in classes)
        return False

    # ---------- begin function body ----------

    sess = _session()

    # 1) First page soup (try to force 100-per page; harmless if ignored)
    sep = "&" if "?" in url else "?"
    first = sess.get(url + f"{sep}players=100", timeout=20)
    soup = _soup(first)

    # 2) Info/metadata
    try:
        info = metadata(soup)
    except Exception:
        # Fallback: very light info extraction
        info = {}
        h1 = soup.find("h1")
        info["fullName"] = h1.get_text(strip=True) if h1 else url.split("/")[-1]
        stats = soup.find("div", class_="tournaments-live-view-content-stats")
        if stats:
            text = stats.get_text(" ", strip=True)
            m = re.search(r"([A-Z][a-z]{2,}\s+\d{1,2},\s+\d{4},\s+\d{1,2}:\d{2}\s*[AP]M)", text)
            if m:
                # keep your ISO style to preserve naming compatibility
                from datetime import datetime as _dt
                try:
                    dt = _dt.strptime(m.group(1), "%b %d, %Y, %I:%M %p")
                    info["startsAt"] = dt.isoformat()
                except Exception:
                    info["startsAt"] = m.group(1)
        info.setdefault("startsAt", "UnknownDate")

    info["id"] = url.rstrip("/").split("/")[-1]

    # 3) Paths and filenames
    path = folder + f"in/cc/{tournament}/"
    os.makedirs(os.path.join(path, "info"), exist_ok=True)
    os.makedirs(os.path.join(path, "results"), exist_ok=True)
    os.makedirs(os.path.join(path, "games"), exist_ok=True)

    name = f"{info['startsAt']} {info['fullName']}.json".replace(":", ";").replace("*", "#").replace("|", "+")
    info_fp    = os.path.join(path, "info",    name)
    results_fp = os.path.join(path, "results", name)
    games_fp   = os.path.join(path, "games",   name)

    # Skip if all files present
    if all(os.path.exists(os.path.join(path, d, name)) for d in ("info", "results", "games")):
        print(f"{name}: Results already downloaded")
        return 0

    utils.dump_json(info, info_fp)

    # 4) Standings / Results (iterate pages until last or repetition)
    results = []
    rank = 0

    # Page 1
    page1_first = _first_username_from_results(soup)
    page_res, rank = _parse_results_page(soup, tournament, rank)
    results.extend(page_res)

    # Subsequent pages
    p = 2
    while True:
        sp, first_name = _fetch_results_page_soup(sess, url, p, prev_first=page1_first if p == 2 else prev_first)
        # If the fetch yields no table, or duplicates first page again, stop
        table_ok = sp and sp.find("table", class_=re.compile(r"tournaments-live-view-results-table"))
        if not table_ok:
            break

        # If this page looks identical to the previous page's first entry, break to avoid loops
        if not first_name:
            break
        if p == 2:
            prev_first = first_name
        else:
            if first_name == prev_first:
                break
            prev_first = first_name

        page_res, rank = _parse_results_page(sp, tournament, rank)
        if not page_res:
            break
        results.extend(page_res)

        # If the currently loaded page is the last (Next disabled), stop
        if _is_last_results_page(sp):
            break

        p += 1

    utils.dump_json(results, results_fp)
    print(f"{name}: Results and Info downloaded")

    # 5) Games / Pairings by round
    games = []

    # number of rounds (Chess.com moved the attribute across containers)
    number_rounds_div = soup.find("div", class_="v5-section")
    if number_rounds_div is None:
        number_rounds_div = soup.find("div", class_="cc-section")
    number_rounds = int(number_rounds_div.get("data-rounds")) if number_rounds_div else 0

    for rnd in range(1, number_rounds + 1):
        # Round page 1
        pr = sess.get(url + f"{sep}round={rnd}&pairings=1", timeout=20)
        r_soup = _soup(pr)
        games.extend(_pairings_table_to_games(r_soup))

        # Iterate subsequent pairings pages until 'Next Page' is disabled or nothing new
        j = 2
        while True:
            # stop if this was last pairings page
            if _is_last_pairings_page(r_soup):
                break
            pr = sess.get(url + f"{sep}round={rnd}&pairings={j}", timeout=20)
            r_soup = _soup(pr)
            page_games = _pairings_table_to_games(r_soup)
            if not page_games:
                break
            games.extend(page_games)
            j += 1

    utils.dump_json(games, games_fp)
    print(f"{name}: Games downloaded")
    return 0



def download_data(arena_type, path, token):
    tournament_links = get_tournament_links(arena_type, path)
    for tournament in tournament_links:
        download_json(arena_type, path, token, tournament)
    return 0


def create_part_json(participation, folder):
    data = {'Early': [], 'Late': [], 'SCC': [], 'TT': []}
    for tournament in participation:
        date = tournament['date'][:10]
        time = tournament['date'][11:16]
        cnt = sum(ts['date'].startswith(date) for ts in participation)
        if 'Early' in tournament['name'] or (cnt > 1 and time < '11:31'):
            data['Early'].append({'x': tournament['date'], 'y': tournament['players']})
        elif 'Late' in tournament['name'] or (cnt > 1 and time >= '11:32'):
            data['Late'].append({'x': tournament['date'], 'y': tournament['players']})
        elif 'Qualifier' in tournament['name'] or 'SCC' in tournament['name']:
            data['SCC'].append({'x': tournament['date'], 'y': tournament['players']})
        else:
            data['TT'].append({'x': tournament['date'], 'y': tournament['players']})
    bg = {'Early': {'R': 237, 'G': 40, 'B': 57, 'A': 0.5}, 'Late': {'R': 0, 'G': 24, 'B': 168, 'A': 0.5},
          'SCC': {'R': 255, 'G': 88, 'B': 0, 'A': 0.5}, 'TT': {'R': 0, 'G': 173, 'B': 131, 'A': 0.5}}
    bd = {'Early': {'R': 255, 'G': 0, 'B': 0, 'A': 0.9}, 'Late': {'R': 0, 'G': 0, 'B': 255, 'A': 0.9},
          'SCC': {'R': 255, 'G': 79, 'B': 0, 'A': 0.9}, 'TT': {'R': 1, 'G': 163, 'B': 104, 'A': 0.9}}

    p_json = {'labels': [tournament['date'] for tournament in participation], 'datasets': []}
    for t_type in data:
        points = {'label': t_type,
                  'data': data[t_type],
                  'backgroundColor': f'rgba({bg[t_type]['R']}, {bg[t_type]['G']}, {bg[t_type]['B']}, {bg[t_type]['A']})',
                  'borderColor': f'rgba({bd[t_type]['R']}, {bd[t_type]['G']}, {bd[t_type]['B']}, {bd[t_type]['A']})',
                  'borderWidth': 2,
                  'yAxisID': 'y1'
                  }
        p_json['datasets'].append(points)
    line = common.add_line(participation)
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
    p_json['datasets'].append(line)
    utils.dump_json(p_json, folder + f'cc/tt/data/participation.json')
    return 0


def shrink(dates):
    base_url = 'https://www.chess.com/tournament/live/'
    return [f'<a href={base_url+date[1]} class={'winner' if date[2] <= 1 else 'loser'}>{date[0][8:10]}.{date[0][5:7]}.{date[0][2:4]}</a>' for date in dates]


def players_list(data, column):
    banned_players = ['Matvei Shcherbin', 'Viacheslav Tilicheev', 'Mark Tran', 'Tobias Hirneise',
                      'Santiago Zapata Charles', 'Daniil Yuffa', 'Vladimir Zakhartsov']
    semi_banned_players = ['Marko Sokac', 'Facundo Quiroga', 'Artem Sadovsky',
                           'Evgeny Levin', 'Evgeny Shaposhnikov', 'Yuri Solodovnichenko', 'Ravil Gabitov']
    inactive_players = ['Pavel Anisimov', 'Vladimir Dobrov', 'Platon Galperin', 'Akshat Chandra', 'Maxim Lugovskoy',
                        'Masoud Mosadeghpour', 'Alexey Maly', 'Khumoyun Begmuratov', 'Volodymyr Vusatiuk',
                        'Vugar Manafov', 'Hrair Simonian', 'Mukhammadali Abdurakhmonov', 'Zaur Mammadov',
                        'Giuseppe Lettieri', 'Alexey Potapov', 'Kamila Hryshchenko', 'Andre Gjestemoen-VonHirsch',
                        'Dragos Ceres', 'Mikheil Mchedlishvili', 'Panagiotis Michelakos', 'Bence Leszko',
                        'Olexiy Bilych']
    multi_players = ['Hans Niemann', 'Khazar Babazada', 'Rustam Khusnutdinov', 'Maxim Dlugy', 'Javokhir Sindarov',
                     'Oleg Vastrukhin', 'Valery Kazakouski', 'Paulius Pultinevicius', 'Aaron Grabinsky',
                     'Cemil Can Ali Marandi', 'Aleksandr Kholin', 'Mark Paragua', 'Rithwik Mathur',
                     'Abhijeet Gupta', 'Liam Vrolijk', 'Yannick Gozzoli', 'Carlos Andres Obregon', 'Shanmukha Meruga']
    sc_b_players = ['Tal Baron', 'David Larino Nieto', 'Aram Hakobyan', 'Jakhongir Vakhidov', 'Sebastian Bogner',
                    'Bahadir Ozen', 'Lucas Liascovich', 'Kanan Garayev']
    sc_c_players = ['Eltaj Safarli', 'Nodirbek Yakubboev', 'Zaven Andriasian', 'Tran Tuan Minh', 'Valery Sviridov',
                    'Shant Sargsyan' 'Varuzhan Akobian', 'Khumoyun Begmuratov', 'Vugar Asadli', 'Christian Braun',
                    'Nicolas Abarca', 'Christopher Guzman', 'Babageldi Annaberdiyev', 'Christopher Repka',
                    'Viacheslav Mikhailov', 'Dominik Horvath', 'Jorge Bobadilla']
    own_players = ['Gata Kamsky', 'Wesley So', 'David Paravyan', 'Nikolas Theodorou', 'Zviad Izoria', 'Denis Kadric',
                   'Pier Luigi Basso', 'Nikoloz Petriashvili', 'Jakub Pulpan', 'Leon Livaic', 'Sergei Azarov',
                   'IM Sophiste2', 'David Gorodetzky', 'Alexandros Dounis', 'Balaji Daggupati', 'Peter Michalik']
    unr_players = ['Baadur Jobava', 'Tigran L. Petrosian']
    prize_players = ['Haik Martirosyan', 'Shamsiddin Vokhidov']
    other_players = ['Nijat Abasov', 'Oleksandr Zubov', 'Brandon Jacobson', 'Dejan Stojanonvski', 'Titas Stremavicius',
                     'Elmar Atakishiyev', 'Ahmad Ahmadzada', 'Pawel Kowalczyk', 'Aaron Jacobson', 'David Gavrilescu',
                     'Juhasz Armin', 'Almas Rakhmatullaev', 'Viktor Matviishen', 'Maxim Lavrov']
    # Sort players by count in descending order
    sorted_players = sorted(data.items(), key=lambda x: (x[1]['count'], x[1]['dates'][0]),
                            reverse=True)
    pl_list = ''
    displayed_counts = set()
    for player, info in sorted_players:
        if (column == 1) or (column == 2 and info['count'] > 1) or (column == 3 and info['count'] == 1):
            if info['count'] not in displayed_counts:
                displayed_counts.add(info['count'])
                group_header = "1 time" if info["count"] == 1 else f"{info['count']} times"
                pl_list += f'<p class="group-header">{group_header}</p>\n'
                # Dates are already sorted, no need to sort again
            dates = ', '.join(shrink(info['dates']))
            if player in banned_players:
                pclass = "player-info banned"
            elif player in semi_banned_players:
                pclass = "player-info semibanned"
            elif player in inactive_players:
                pclass = "player-info inactive"
            elif player in multi_players:
                pclass = "player-info multi"
            elif player in sc_b_players:
                pclass = "player-info sc_b"
            elif player in sc_c_players:
                pclass = "player-info sc_c"
            elif player in own_players:
                pclass = "player-info own"
            elif player in unr_players:
                pclass = "player-info unrelated"
            elif player in prize_players:
                pclass = "player-info prize"
            elif player in other_players:
                pclass = "player-info other"
            else:
                pclass = 'player-info'
            pl_list += f'<p class="{pclass}">{player}: {dates}</p>\n'
    return pl_list


def calc_best(data, folder):
    perf = [
        {**tournament, 'name': player}
        for player, results in {common.crop_key(key, 'long'): value for key, value in data.items()}.items()
        for tournament in results['score']
    ]

    html_content = '''
    <html>
    <head>
        <title>Highest Scores</title>
        <style>
            .container {
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 10px;
            }
            h3 {
                text-align: center;
                margin-top: 0;
                margin-bottom: 10px;
                text-decoration: underline;
            }
            .t-header {
                text-align: center;
                margin-top: 15px;
                margin-bottom: 10px;
                font-weight: bold;
                color: #5D9948;
            }
            .group-header {
                font-weight: bold;
                margin-top: 5px;
                margin-bottom: 5px;
            }
            .player-info {
                margin-left: 20px;
                margin-top: 1px;
                margin-bottom: 1px;
            }
            .banned {
                text-decoration: line-through;
            }
            .semibanned {
                text-decoration: dashed line-through;
            }
            .inactive {
                text-decoration: dotted line-through;
            }
            .multi {
                text-decoration: underline #FF0000;
            }
            .sc_b {
                text-decoration: underline #DD4124;
            }
            .sc_c {
                text-decoration: dashed underline #DD4124;
            }
            .own {
                text-decoration: dotted underline #FEDF00;
            }
            .unrelated {
                text-decoration: underline #FEDF00;
            }
            .other {
                text-decoration: underline #FEDF00;
            }
            .prize {
                text-decoration: dotted underline #FFBE98;
            }
        </style>
    </head>'''
    html_content += '<body>'
    titles = {11: 'since Oct 20, 2020 + once Mar 7, 2017',
              10: 'Apr 4, 2017 - Dec 3, 2019, May 5-26, 2020, and swiss part of Speed Chess Championship Jun 2, 2020 - Oct 13, 2020',
              9: 'Oct 2014 to Feb 7, 2017 (excl. Jan 27, 2015), and Jan 7 - Apr 28, 2020'}
    for rounds in [11, 10, 9]:
        html_content += f'<div class="t-header">{rounds} rounds: {titles[rounds]}</div>'
        html_content += '<div class="container"><div>'
        highest_scores_column_1 = [rounds, rounds - 0.5]
        highest_scores_column_2 = [rounds - 1.0]
        scores_data = {score: {} for score in highest_scores_column_1 + highest_scores_column_2}
        for pr in perf:
            player = pr['name']
            score = pr['points']
            date = pr['date'][:10]
            if score in scores_data:
                if (rounds == 11 and (date > '2020-10-16' or date == '2017-03-07')) or (rounds == 10 and ('2017-04-01' < date < '2019-12-31' or '2020-05-01' < date < '2020-10-16')) or (rounds == 9 and (date < '2017-02-20' or '2020-01-01' < date < '2020-04-29')):
                    # 11 rounds
                    if player not in scores_data[score]:
                        scores_data[score][player] = {'count': 0, 'dates': []}
                    scores_data[score][player]['count'] += 1
                    scores_data[score][player]['dates'].append((date, pr['id'], pr['rank']))
        # Processing for scores in highest_scores_column_1 (R, R-0.5)
        for score in highest_scores_column_1:
            if score in scores_data:
                html_content += f'<div><h3>{score} points</h3>\n'
                html_content += players_list(scores_data[score], 1)
                html_content += '</div>\n'
    # Processing for scores in highest_scores_column_2 (R-1)
        html_content += '''</div><div>'''
        # Players achieving R-1 points more than once
        html_content += f'<div><h3>{rounds - 1} points</h3>\n'
        html_content += players_list(scores_data[rounds - 1], 2)
        html_content += '</div>\n</div>\n<div class="column">'
        # Players achieving '10 points' exactly once
        html_content += players_list(scores_data[rounds - 1], 3)
        html_content += '</div>\n</div>\n</div></div>'
    html_content += '</div>\n</div></div>\n'

    html_content += ('Baadur Jobava also won both Titled Tuesdays on Jan 27, 2015 with a perfect score of <a href=https://www.chess.com/tournament/live/-titled-tuesday-32-blitz-459814 class=''winner''>4/4</a> and <a href=https://www.chess.com/tournament/live/-titled-tuesday-32-blitz-483353 class=''winner''>7/7</a>.<p>'
                     '<div class="t-header">Fair Play</div><p>'
                     'The following prize-winning players were disqualified by Chess.com and had their account closed during the tournament or shortly after (X): Matvei Shcherbin, Viacheslav Tilicheev (both 02.06.15), Mark Tran (01.09.15), Tobias Hirneise (07.11.17), '
                     'Santiago Zapata Charles (17.04.18), Daniil Yuffa (06.11.18), Javokhir Sindarov, Vladimir Zakhartsov, and Kanan Garayev (all three 02.04.19), so they are excluded from the winner statistics.<p>'
                     'These players Chess.com accounts were closed shortly after their successful performances on Titled Tuesdays; however, Chess.com did not change the results of the tournaments in the corresponding press releases. Their results remain presented in the winners statistics. '
                     'Players (their last game date) (X): Marko Sokac (06.10.15), Facundo Quiroga (12.10.15), Artem Sadovsky (09.11.15), Ravil Gabitov (05.01.16), Evgeny Levin (07.02.17), Evgeny Shaposhnikov (23.02.17), Yuri Solodovnichenko (05.12.17).<p>'
                     'Players who became inactive shortly after their success in Titled Tuesdays (S): Akshat Chandra (17.04.18), Alexey Potapov (05.03.19), Pavel Anisimov (23.03.21), Bence Leszko (29.03.21), Mukhammadali Abdurakhmonov (21.09.21), Vugar Manafov (09.12.21), Alexey Maly (11.01.22), Panagiotis Michelakos (17.02.22), Maxim Lugovskoy (21.02.22), Kamila Hryshchenko (08.03.22), Vladimir Dobrov (19.04.22), Mikheil Mchedlishvili (14.06.22), Giuseppe Lettieri (12.07.22), Dragos Ceres (27.09.22), Volodymyr Vusatiuk (01.11.22), Masoud Mosadeghpour (31.01.23), Andre Gjestemoen-VonHirsch (21.02.23), Zaur Mammadov (24.04.23), Olexiy Bilych (09.05.23), Hrair Simonian (20.06.23), Platon Galperin (19.07.23). <p>'
                     'Players with multiple inactive or closed accounts (M): Hans Niemann (HansCoolNiemann, IMHansNiemann, HansOnTwitch), Javokhir Sindarov (maloy07, Wonderboy05, Javokhir_Sindarov05), Abhijeet Gupta (abhijeetgupta1016, abhijeetgupta), Yannick Gozzoli (Siana, Nouki, Noukii), Mark Paragua (Hamonde, MarkParagua, Mark_Paragua_PCAP), Valery Kazakouski (Gloomy_Wanderer, Experience_Chess, ContrVersia), Paulius Pultinevicius (pultineviciuspaulius, Pultis, Nemegejas), Liam Vrolijk (Vrolijk, LiamVrolijk), Maxim Dlugy (Dlugy, MaximDlugy, chessonado), Cemil Can Ali Marandi (CemilCan, PrettyPrincess2002, Last7Samurai), Rustam Khusnutdinov (RD4ever, LordBalrog, GiantThresher), Carlos Andres Obregon (Sharpchess22, GMCarlosAObregon), Khazar Babazada (DangerousPlayer1st, KhazarBabazada, anon6121824), Aaron Grabinsky (Gabrinsky, Silent_Terror, FastChance, Tactrics), Oleg Vastrukhin (vastra91, kuban1991, demon64fields), Aleksandr Kholin (AleksandrKholin, Aleksandr_Kholin, Alexandr_Kholin), Rithwik Mathur (rithwik2002, rithwik1212, 2L8IWUN), Shanmukha Meruga (gmshanmeruga, NMShanMeruga, BuyBoxBandit).<p>'
                     'Players whose accounts were closed following their successful Titled Tuesday performance are now competing with a second chance account (B): Lucas Liascovich (10.06.15), Bahadir Ozen (19.08.15), Tal Baron (06.10.15), David Larino Nieto (02.02.16), Jakhongir Vakhidov (04.11.16), Aram Hakobyan (10.07.18), Jaime Santos Latasa (15.09.18), Sebastian Bogner (19.09.18), Kanan Garayev (02.04.19).<p>'
                     'Players whose accounts were inactive after their successful Titled Tuesday performance are now competing with a second chance account (C): Varuzhan Akobian (02.02.16), Jorge Bobadilla (03.05.16), Tran Tuan Minh (25.08.16), Eltaj Safarli (13.02.17), Vugar Asadli (05.03.19), Christian Braun (08.01.20), Shant Sargsyan (22.04.20), Zaven Andriasian (23.04.20), Viacheslav Mikhailov (05.05.20), Christopher Guzman (15.07.20), Christopher Repka (04.08.20), Nodirbek Yakubboev (28.12.21), Dominik Horvath (14.02.22), Valery Sviridov (25.02.22), Nicolas Abarca (17.07.22), Babageldi Annaberdiyev (28.12.22), Khumoyun Begmuratov (04.02.23).<p>'
                     'Players whose accounts have been closed for reasons unrelated to Titled Tuesday (X): Tigran L. Petrosian (30.09.20), Baadur Jobava (11.02.23).<p>'
                     'Players who have a history of closed or inactive accounts (?): Nijat Abasov (nijat_a, AbasovN), Oleksandr Zubov (Zubov_Alexander, Alexander_Zubov), Brandon Jacobson (iamastraw, BrandonJacobson), Dejan Stojanonvski (ChessTrener, TrainerDejan), Titas Stremavicius (JustaTrickstar, ViciousTitas, komandoras123), Elmar Atakishiyev (Atakishiyev04, EAtakishiyev11), Ahmad Ahmadzada (ahmadzada13, AhmadzadaA), Pawel Kowalczyk (KrolPawel92OnTwitch, P_Kowalczyk), Aaron Jacobson (1random, WorriedEgg), David Gavrilescu (anon219, DavidGavrilescu18), Juhasz Armin (DrHolmes13, CentrumSakkiskola), Almas Rakhmatullaev (AlmasChampion1, AlmasRakhmatullaev), Viktor Matviishen (ViktorMatviishen, Viktor_Matviishen), Maxim Lavrov (maximlavrov, Lavrov_Maxim), Ivan Cheparinov (Chepaschess, GMCheparinov).<p>'
                     'Players believed to be prohibited from participating in prize tournaments (!): Haik Martirosyan (Micki-taryan), Shamsiddin Vokhidov (Vokhidov11, Shield12).<p>'
                     'Players who closed their account(s) themselves (*): Gata Kamsky (gkchesstiger, GataKamsky1974, TigrVShlyape), Wesley So (gmwesley_so, GMWSO), David Paravyan (David_Paravyan, dropstoneDP), Nikolas Theodorou (OminousOmen, NikoTheodorou), Zviad Izoria (Izoria123), Sergei Azarov (SergeiAza, Sereiaza), Pier Luigi Basso (Maybe00), Denis Kadric (TheFlaminGM, Kiborg95), Leon Livaic (Bulldog167, Elsa167), Nikoloz Petriashvili (Petriashvili02, super_emi_26), Jakub Pulpan (PulpanJ, JakubPulpan), David Gorodetzky (pKiLz5Rn9b, pheonixking2000), Alexandros Dounis (x-5963514717, Maskless_Beast), Balaji Daggupati (cool4chess, chessintuit), Peter Michalik (Lunaticx), Ruslan Ponomariov (NDePinEsPeRG, R-Ponomariov, MashaPutina1985), IM Sophiste2 (03.05.16).')
    html_content += '</body></html>'

    # Write to an HTML file
    with open(folder + 'cc/tt/data/highest_scores.html', 'w') as file:
        file.write(html_content)

    return 0


def colormap(performances, a):
    cmap = {'Magnus Carlsen':          f'rgba(182,  12,  47, {a})',
            'Hikaru Nakamura':         f'rgba( 10,  49,  97, {a})',
            'Daniel Naroditsky':       f'rgba(179,  25,  66, {a})',
            'Daniel Naroditsky (d)':   f'rgba(179,  25,  66, {a})',
            'Olexandr Bortnyk':        f'rgba(255, 215,   0, {a})',
            'Alireza Firouzja':        f'rgba( 35, 159,  64, {a})',
            'Jose Martinez Alcantara': f'rgba(  0, 104,  71, {a})',
            'Andrew Tang':             f'rgba( 95,  37, 124, {a})',
            'Nihal Sarin':             f'rgba(255, 103,  31, {a})',
            'Dmitry Andreikin':        f'rgba(  0, 171, 194, {a})',
            'Le Tuan Minh':            f'rgba(218,  37,  29, {a})',
            'Sergei Zhigalko':         f'rgba(105,  95,  52, {a})',
            'Yoseph Theolifus Taher':  f'rgba(246, 141, 145, {a})',
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
            'Javokhir Sindarov':       f'rgba(136, 176,  75, {a})',
            'Ediz Gurel':              f'rgba(227,  10,  23, {a})'}
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
        key=lambda x: (x['score'], -x['rank'], x['date']),
        reverse=True
    )[:n]

    b_json = {
        'labels': [performance['player'] + f' ({performance['date'].split('T')[0]}, {performance['rank']} place)' for performance in performances],
        'datasets': [
            {
                'label': 'Top-40 Scores',
                'data': [performance['score'] for performance in performances],
                'backgroundColor': colormap(performances, 1.0),
                'borderColor': "rgb(0, 0, 0)",
                'borderWidth': 1
            }
        ]
    }
    utils.dump_json(b_json, folder + f'cc/{arena_type}/data/best.json')
    return 0
