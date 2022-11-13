from os import environ
from requests import get
from json import dumps, loads
from dotenv import load_dotenv
from datetime import datetime, timedelta

from arbitrage import is_arbitrage, arbitrage_profit


def parse_commence_time(commence_time):
    start_time_lst = commence_time.split("T")
    start_time_lst[1] = start_time_lst[1][:-1]
    parsed_commence_time = start_time_lst[0] + " " + start_time_lst[1]
    dt = datetime.strptime(parsed_commence_time, "%Y-%m-%d %H:%M:%S")
    dt = dt + timedelta(hours=1)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def serialize_arbs(arbs):
    res_lst = []
    for arb_dict in arbs:
        arb_str = dumps(arb_dict)
        res_lst.append(arb_str)
    return res_lst


def deserialize_arbs(serialized_arbs):
    res_lst = []
    for arb_str in serialized_arbs:
        arb_dict = loads(arb_str)
        res_lst.append(arb_dict)
    return res_lst


def get_the_odds_api_data():
    load_dotenv()
    key = str(environ.get("THE_ODDS_API_KEY"))

    r = get("https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={0}&regions=eu&markets=h2h"
                     .format(key))
    return r.headers, r.json()


def get_all_arbs():
    headers, the_odds_api_match_json = get_the_odds_api_data()
    res = []

    for match in the_odds_api_match_json:
        # There can't be an arbitrage if there is less than two bookmakers on a match
        if len(match["bookmakers"]) < 2:
            continue
        team_a = match["home_team"]
        team_b = match["away_team"]
        commence_time = match["commence_time"]
        category = match["sport_title"]

        bookmaker_names = []
        odds_dict = {
            team_a: [],
            team_b: []
        }
        for bookmaker in match["bookmakers"]:
            bookmaker_names.append(bookmaker["title"])
            for market in bookmaker["markets"]:
                if market["key"] != "h2h":
                    continue
                for i, outcome in enumerate(market["outcomes"]):
                    # TODO: We are ignoring draws for now but will implement in the future
                    if outcome["name"] == "Draw":
                        continue
                    odds_dict[outcome["name"]].append(outcome["price"])
        if len(odds_dict) != 2:
            print("Odds dictionary is not the expected length.")
        for i, o_a in enumerate(odds_dict[team_a]):
            for j, o_b in enumerate(odds_dict[team_b]):
                if i == j:
                    # No arbitrage 'within one bookmaker' (even if there is they probably won't allow you to bet on both)
                    continue
                if is_arbitrage(o_a, o_b):
                    arb_dict = {
                        "category": category,
                        "team_a": team_a,
                        "team_b": team_b,
                        "bookmaker_a": bookmaker_names[i],
                        "bookmaker_b": bookmaker_names[j],
                        "odds_a": o_a,
                        "odds_b": o_b,
                        "profit": round(arbitrage_profit(o_a, o_b, 100), 2),
                        "start_time": parse_commence_time(commence_time)
                    }
                    res.append(arb_dict)
    return headers["x-requests-remaining"], res


def get_fake_arbs():
    res = []
    commence_time = "2021-09-10T00:20:00Z"
    for i in range(50):
        arb_dict = {
            "category": "LEAGUE OF LEGENDS",
            "team_a": "Team Super Cool DRX",
            "team_b": "Team Super Awesome T1",
            "bookmaker_a": "Bet365",
            "bookmaker_b": "Betsson",
            "odds_a": i,
            "odds_b": 1.5,
            "profit": 13.37,
            "start_time": parse_commence_time(commence_time)
        }
        res.append(arb_dict)
    return 1337, res

