from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap
from threading import Thread, Lock
from time import sleep
from datetime import timedelta, datetime, timezone

from the_odds_api_parser import get_all_arbs, get_fake_arbs
from arbitrage import arbitrage_profit, arbitrage_bets

flask_app = Flask(__name__)
Bootstrap(flask_app)

global_arbs = []
global_arb_lock = Lock()
global_hours_delta = 3

global_next_update = datetime.now(tz=timezone.utc) + timedelta(hours=global_hours_delta)


@flask_app.route('/', methods=['GET'])
def index():
    global_arb_lock.acquire()
    arbs = global_arbs
    global_arb_lock.release()
    time_until_next_update = global_next_update - datetime.now(tz=timezone.utc)
    return render_template("index.html", arbs=arbs,
                           seconds_until_refresh=int(time_until_next_update.total_seconds() + 5))


@flask_app.route('/new_investment', methods=['POST'])
def new_investment():
    investment = int(request.form["new_investment"])
    odds_a = float(request.form["odds_a"])
    odds_b = float(request.form["odds_b"])
    profit = round(arbitrage_profit(odds_a, odds_b, investment), 2)
    to_bet = arbitrage_bets(odds_a, odds_b, investment)
    return jsonify({
        "profit": profit,
        "to_bet_a": round(to_bet[0], 2),
        "to_bet_b": round(to_bet[1], 2)
    })


@flask_app.route('/select_arb', methods=['POST'])
def select_arb():
    select_arb_index = int(request.form["select_arb_index"])
    global_arb_lock.acquire()
    all_arbs = global_arbs
    global_arb_lock.release()
    data = all_arbs[select_arb_index]
    return jsonify(data)


def update_global_args():
    global global_arbs
    global global_next_update
    while True:
        sleep_seconds = (global_next_update - datetime.now(tz=timezone.utc)).total_seconds()
        print("[Update Thread] Going to sleep for {0} seconds".format(sleep_seconds))
        sleep(sleep_seconds)
        print("[Update Thread] Done sleeping")
        print("[Update Thread] Acquiring lock")
        global_arb_lock.acquire()
        print("[Update Thread] Grabbing Arbs from API")
        global_arbs = get_all_arbs()
        print("[Update Thread] Releasing lock")
        global_arb_lock.release()
        global_next_update = datetime.now(tz=timezone.utc) + timedelta(hours=global_hours_delta)
        print("[Update Thread] Next update will be at {0}".format(global_next_update))


def run():
    global global_arbs
    global_arbs = get_all_arbs()
    update_thread = Thread(target=update_global_args)
    #server_thread = Thread(target=flask_app.run)
    update_thread.start()
    #server_thread.start()

