from os import environ
from requests import get
from json import dumps, loads
from dotenv import load_dotenv
from datetime import datetime, timedelta

from arbitrage import is_arbitrage, arbitrage_profit


bookmaker_links = {
    "1xBet": "https://1xbet.com/",
    "888sport": "https://www.888sport.com/",
    "Betclic": "https://www.betclic.com/",
    "Betfair": "https://www.betfair.com/",
    "BetOnline.ag": "https://www.betonline.ag/",
    "Betsson": "https://www.betsson.com/",
    "Pinnacle": "https://www.pinnacle.se/en/",
    "Marathon Bet": "https://www.marathonbet.com/",
    "Nordic Bet": "https://www.nordicbet.com/",
    "Unibet": "https://www.unibet.com/",
    "MyBookie.ag": "https://www.mybookie.ag/",
    "Intertops": "https://everygame.eu/",
    "Matchbook": "https://www.matchbook.com/",



}

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
            team_b: [],
            "Draw": [],
        }
        for bookmaker in match["bookmakers"]:
            bookmaker_names.append(bookmaker["title"])
            for market in bookmaker["markets"]:
                if market["key"] != "h2h":
                    continue
                for i, outcome in enumerate(market["outcomes"]):
                    odds_dict[outcome["name"]].append(outcome["price"])
        # Now we go through all outcomes and check for arbitrage
        for i, o_a in enumerate(odds_dict[team_a]):
            for j, o_b in enumerate(odds_dict[team_b]):
                if odds_dict["Draw"]:
                    for k, o_draw in enumerate(odds_dict["Draw"]):
                        if i == j or i == k or j == k:
                            # No arbitrage 'within one bookmaker'
                            # (even if there is they probably won't allow you to bet on both)
                            continue
                        if is_arbitrage(o_a, o_b, o_draw):
                            arb_dict = {
                                "category": category,
                                "team_a": team_a,
                                "team_b": team_b,
                                "bookmaker_a": bookmaker_names[i],
                                "bookmaker_b": bookmaker_names[j],
                                "bookmaker_draw": bookmaker_names[k],
                                #"bookmaker_a_link": bookmaker_links[bookmaker_names[i]],
                                #"bookmaker_b_link": bookmaker_links[bookmaker_names[j]],
                                #"bookmaker_draw_link": bookmaker_links[bookmaker_names[k]],
                                "odds_a": o_a,
                                "odds_b": o_b,
                                "odds_draw": o_draw,
                                "profit": round(arbitrage_profit(o_a, o_b, 100, o_draw), 2),
                                "start_time": parse_commence_time(commence_time),
                            }
                            res.append(arb_dict)
                else:
                    if i == j:
                        # No arbitrage 'within one bookmaker'
                        # (even if there is they probably won't allow you to bet on both)
                        continue
                    if is_arbitrage(o_a, o_b):
                        arb_dict = {
                            "category": category,
                            "team_a": team_a,
                            "team_b": team_b,
                            "bookmaker_a": bookmaker_names[i],
                            "bookmaker_b": bookmaker_names[j],
                            #"bookmaker_a_link": bookmaker_links[bookmaker_names[i]],
                            #"bookmaker_b_link": bookmaker_links[bookmaker_names[j]],
                            "odds_a": o_a,
                            "odds_b": o_b,
                            "profit": round(arbitrage_profit(o_a, o_b, 100), 2),
                            "start_time": parse_commence_time(commence_time),
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
            "bookmaker_a": "Betfair",
            "bookmaker_b": "Betsson",
            "bookmaker_draw": "Matchbook",
            "bookmaker_a_link": bookmaker_links["Betfair"],
            "bookmaker_b_link": bookmaker_links["Betsson"],
            "bookmaker_draw_link": bookmaker_links["Matchbook"],
            "odds_a": i,
            "odds_b": 1.5,
            "profit": 13.37,
            "start_time": parse_commence_time(commence_time)
        }
        if i % 2 == 0:
            arb_dict["bookmaker_draw"] = "Matchbook"
            arb_dict["odds_draw"] = 3.0
            arb_dict["profit"] = 42.69
        res.append(arb_dict)
    return 1337, res


if __name__ == "__main__":
    arbs = get_all_arbs()

