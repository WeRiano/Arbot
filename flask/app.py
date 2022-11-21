from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap
from multiprocessing import Process, Queue
from redis import StrictRedis
from threading import Thread
from time import sleep
from datetime import timedelta, datetime, timezone
from pytz import utc

from the_odds_api_parser import get_all_arbs, get_fake_arbs, serialize_arbs, deserialize_arbs
from arbitrage import arbitrage_profit, arbitrage_bets


# Initialization stuff

arb_update_delta_hours = 2
next_update_str_format = "%Y-%m-%d %H:%M:%S"

# Function pointer that defines if we are using real or fake data
#get_arbs = get_all_arbs
get_arbs = get_fake_arbs

flask_app = Flask(__name__)
Bootstrap(flask_app)
redis = StrictRedis(host="redis", port=6379, decode_responses=True)
if not redis.exists("next_update"):
    redis.set("next_update",
              (datetime.now(tz=timezone.utc) +
               timedelta(hours=arb_update_delta_hours + 1)).strftime(next_update_str_format))
if not redis.exists("arbs"):
    remaining_requests_init, arbs_init = get_arbs()
    redis.rpush("arbs", *serialize_arbs(arbs_init))
    redis.set("remaining_requests", remaining_requests_init)


def get_arbs_from_redis():
    arbs_length = redis.llen("arbs")
    serialized_arbs = redis.lrange("arbs", 0, arbs_length - 1)
    return deserialize_arbs(serialized_arbs)


@flask_app.route('/', methods=['GET'])
def index():
    next_update = datetime.strptime(redis.get("next_update"), next_update_str_format)
    next_update = utc.localize(next_update)
    now = datetime.now(tz=timezone.utc) + timedelta(hours=1)
    if next_update < now:
        # Next update is now! Let us calculate when the next update is ...
        next_update = next_update + timedelta(hours=arb_update_delta_hours)
        next_update_str = next_update.strftime(next_update_str_format)
        redis.set("next_update", next_update_str)

        # ... and actually update
        remaining_requests, arbs = get_arbs()
        redis.delete("arbs")
        redis.rpush("arbs", *serialize_arbs(arbs))
        redis.set("remaining_requests", remaining_requests)
    else:
        # We are not updating now, we grab arbs from storage
        arbs = get_arbs_from_redis()
        remaining_requests = redis.get("remaining_requests")
        next_update_str = next_update.strftime(next_update_str_format)

    ms_until_next_update = int((next_update - now).total_seconds() * 1000)
    return render_template("index.html", arbs=arbs, ms_until_refresh=ms_until_next_update, next_update=next_update_str,
                           remaining_requests=remaining_requests)


@flask_app.route('/new_investment', methods=['POST'])
def new_investment():
    investment = int(request.form["new_investment"])
    odds_a = float(request.form["odds_a"])
    odds_b = float(request.form["odds_b"])
    odds_draw = request.form["odds_draw"]
    if odds_draw == "":
        odds_draw = None
    else:
        odds_draw = float(odds_draw)
    profit = round(arbitrage_profit(odds_a, odds_b, investment, odds_draw), 2)
    to_bet = arbitrage_bets(odds_a, odds_b, investment, odds_draw)
    return jsonify({
        "profit": profit,
        "to_bet_a": round(to_bet[0], 2),
        "to_bet_b": round(to_bet[1], 2),
        "to_bet_draw": "" if odds_draw is None else round(to_bet[2], 2)
    })


@flask_app.route('/select_arb', methods=['POST'])
def select_arb():
    select_arb_index = int(request.form["select_arb_index"])
    arbs = get_arbs_from_redis()
    data = arbs[select_arb_index]

    if "odds_draw" in data:
        to_bet = arbitrage_bets(data["odds_a"], data["odds_b"], 100, data["odds_draw"])
        data["to_bet_draw"] = round(to_bet[2], 2)
    else:
        to_bet = arbitrage_bets(data["odds_a"], data["odds_b"], 100)
        data["to_bet_draw"] = ""
        data["odds_draw"] = ""
        data["bookmaker_draw"] = ""
    data["to_bet_a"] = round(to_bet[0], 2)
    data["to_bet_b"] = round(to_bet[1], 2)
    return jsonify(data)


if __name__ == "__main__":
    flask_app.run()

