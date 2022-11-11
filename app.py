from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap
from threading import Thread, Lock
import time

from the_odds_api_parser import get_all_arbs, get_fake_arbs
from arbitrage import arbitrage_profit, arbitrage_bets

app = Flask(__name__)
Bootstrap(app)
global_arbs = []
arb_lock = Lock()


@app.route('/', methods=['GET'])
def index():
    arb_lock.acquire()
    arbs = global_arbs
    arb_lock.release()
    return render_template("index.html", arbs=arbs)


@app.route('/new_investment', methods=['POST'])
def new_investment():
    print("New investment!")
    print(request.form["odds_a"])
    print(request.form["odds_b"])
    investment = int(request.form["new_investment"])
    odds_a = float(request.form["odds_a"])
    odds_b = float(request.form["odds_b"])
    profit = arbitrage_profit(odds_a, odds_b, investment)
    to_bet = arbitrage_bets(odds_a, odds_b, investment)
    return jsonify({
        "profit": profit,
        "to_bet_a": to_bet[0],
        "to_bet_b": to_bet[1]
    })


@app.route('/select_arb', methods=['POST'])
def select_arb():
    print("Select arb!")
    select_arb_index = int(request.form["select_arb_index"])
    arb_lock.acquire()
    all_arbs = global_arbs
    arb_lock.release()
    data = all_arbs[select_arb_index]
    return jsonify(data)


def update_global_args():
    global global_arbs
    while True:
        print("[Update Thread] Going to sleep")
        time.sleep(4 * 60 * 60)
        print("[Update Thread] Done sleeping")
        print("[Update Thread] Acquiring lock")
        arb_lock.acquire()
        global_arbs = get_all_arbs()
        print("[Update Thread] Releasing lock")
        arb_lock.release()


if __name__ == "__main__":
    global_arbs = get_fake_arbs()
    update_thread = Thread(target=update_global_args)
    server_thread = Thread(target=app.run)
    update_thread.start()
    server_thread.start()

