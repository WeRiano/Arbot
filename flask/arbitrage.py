"""
    How can we spot arbitrage in betting?

    For a bet to be profitable regardless of outcome, two inequalities must hold

        m_A + m_B < win_A (1)
        m_A + m_B < win_B (2)

    Where m_A and m_B is the amount of money bet on outcome A and B respectively,
    and win_A and win_B is the amount of money won if outcome A and B comes to pass, respectively.

    We know that win_A = m_A * O_A where O_A is the given odds of outcome A. The same obviously also goes for outcome B.
    This gives us

        m_A + m_B < m_A * O_A (3)
        m_A + m_B < m_B * O_B (4)

    Now comes the "tricky part" (intuitively). If we let m_A = I / O_A and m_B = I / O_B where I is some arbitrary
    amount of money, inequalities (3) and (4) become

        I / O_A + I / O_B < (I / O_A) * O_A (5)
        I / O_A + I / O_B < (I / O_B) * O_B (6)

    which simplifies to

        1 / O_A + 1 / O_B < 1 (5)
        1 / O_A + 1 / O_B < 1 (6)

    Note that inequalities 5 and 6 are the same. This means that as long as this __one__ inequality holds, we have a bet
    that we can make money on regardless of outcome. Note that this inequality is unaffected by I, which in our
    case is the amount of money that we are willing to 'risk' or 'invest' into our surebet (which makes sense!).
    However, again, we must remember that the amount of money bet on outcome A and B respectively __must be__

        m_A = I / O_A

    and

        m_B = I / O_B

    -------------------------------------------------------------------------------------------------------------------

    How much money will we make on a surebet?

    Our profit is calculated as the amount of money we win subtracted by the amount of money we spend, i.e

        P = win_A - m_A + m_B (7)

    or

        P = win_B - m_A + m_B (8)

    depending on which outcome comes to pass (it will either be A or B, always).

    Using our previous substitutions we get

        win_A = m_A * O_A = (I / O_A) * O_B = I

    and

        win_B = m_B * O_B = (I / O_B) * O_B = I

    which means that

        win_A = win_B = I

    This transforms both equation (7) and (8) into

        P = I - m_A + m_B
"""


def is_arbitrage(odds_a, odds_b, odds_draw=None):
    if odds_draw is None:
        return 1 / odds_a + 1 / odds_b < 1
    return 1 / odds_a + 1 / odds_b + 1 / odds_draw < 1


def arbitrage_bets(odds_a, odds_b, investment, odds_draw=None):
    if odds_draw is None:
        return investment / odds_a, investment / odds_b
    return investment / odds_a, investment / odds_b, investment / odds_draw


def arbitrage_profit(odds_a, odds_b, investment, odds_draw=None):
    bets = arbitrage_bets(odds_a, odds_b, investment, odds_draw)
    if len(bets) == 2:
        return investment - (bets[0] + bets[1])
    return investment - (bets[0] + bets[1] + bets[2])


if __name__ == "__main__":
    a = 1.80
    b = 2.30
    spending = 5000
    print(is_arbitrage(a, b))
    print(arbitrage_bets(a, b, spending))
    print(arbitrage_profit(a, b, spending))