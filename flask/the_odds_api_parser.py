import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone

from arbitrage import is_arbitrage, arbitrage_profit


def parse_commence_time(commence_time):
    start_time_lst = commence_time.split("T")
    start_time_lst[1] = start_time_lst[1][:-1]
    parsed_commence_time = start_time_lst[0] + " " + start_time_lst[1]
    return parsed_commence_time


def get_delta_time_minutes(match_time):
    match_list = match_time.split("T")
    match_date_list = match_list[0].split("-")
    match_time_list = match_list[1].split(":")
    match_time_list[2] = match_time_list[2][:-1]
    datetime_now = datetime.now(tz=timezone.utc)
    datetime_match = datetime(int(match_date_list[0]), int(match_date_list[1]), int(match_date_list[2]),
                              int(match_time_list[0]), int(match_time_list[1]), int(match_time_list[2]),
                              tzinfo=timezone.utc)
    delta = datetime_match - datetime_now
    return delta.total_seconds() / 60


def fetch_the_odds_api_matches():
    load_dotenv()
    key = str(os.environ.get("THE_ODDS_API_KEY"))

    r = requests.get("https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={0}&regions=eu&markets=h2h"
                     .format(key))
    return r.json()


def get_all_arbs():
    the_odds_api_match_json = fetch_the_odds_api_matches()
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
                    # print("----------- Arbitrage spotted! ----------- ")
                    # print("The category is {0}".format(category))
                    # print("Team {0} versus {1}".format(team_a, team_b))
                    # print("On bookmakers {0} and {1}".format(bookmaker_names[i], bookmaker_names[j]))
                    # print("With odds {0} versus {1}".format(o_a, o_b))
                    # print("Where the total profit is {0}%".format(arbitrage_profit(o_a, o_b, 100)))
                    # print("The match is due in {0} minutes".format(get_delta_time_minutes(start_time)))
                    arb_dict = {
                        "category": category,
                        "team_a": team_a,
                        "team_b": team_b,
                        "bookmaker_a": bookmaker_names[i],
                        "bookmaker_b": bookmaker_names[j],
                        "odds_a": o_a,
                        "odds_b": o_b,
                        "profit": arbitrage_profit(o_a, o_b, 100),
                        "start_time": parse_commence_time(commence_time)
                    }
                    res.append(arb_dict)
    return res


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
    return res
