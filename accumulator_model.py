"""Poisson model for the 24 Oct 2026 fixtures and two accumulator slips.

Expected goals (lambda) per side are estimated from public previews:
bookmaker 1X2 / totals prices, model win probabilities (Statz, Dimers,
Forebet, Kalshi, AccuScore), season goals for/against and team news.
"""
from math import exp, factorial, prod

MAX_GOALS = 10
MARGIN = 1.06  # typical bookmaker overround applied to fair odds

# (home, away, lambda_home, lambda_away)
MATCHES = {
    "como_sassuolo": ("Como", "Sassuolo", 2.00, 0.95),
    "cagliari_bologna": ("Cagliari", "Bologna", 1.05, 1.10),
    "racing_espanyol": ("Racing Santander", "Espanyol", 1.35, 1.15),
    "coventry_fulham": ("Coventry", "Fulham", 1.25, 1.45),
    "arsenal_everton": ("Arsenal", "Everton", 1.75, 0.60),
    "paderborn_hsv": ("Paderborn", "Hamburger SV", 1.40, 1.25),
    "koln_schalke": ("Köln", "Schalke", 1.30, 0.90),
    "mainz_werder": ("Mainz", "Werder Bremen", 1.75, 1.20),
    "augsburg_union": ("Augsburg", "Union Berlin", 1.65, 1.10),
    "leipzig_elversberg": ("RB Leipzig", "Elversberg", 2.40, 1.00),
}


def pois(k, lam):
    return exp(-lam) * lam**k / factorial(k)


def grid(lh, la):
    return {(h, a): pois(h, lh) * pois(a, la)
            for h in range(MAX_GOALS) for a in range(MAX_GOALS)}


def prob(g, cond):
    return sum(p for (h, a), p in g.items() if cond(h, a))


MARKETS = {
    "1": lambda h, a: h > a,
    "X": lambda h, a: h == a,
    "2": lambda h, a: h < a,
    "1X": lambda h, a: h >= a,
    "X2": lambda h, a: h <= a,
    "O1.5": lambda h, a: h + a > 1,
    "O2.5": lambda h, a: h + a > 2,
    "U2.5": lambda h, a: h + a < 3,
    "U3.5": lambda h, a: h + a < 4,
    "BTTS": lambda h, a: h > 0 and a > 0,
    "1&O1.5": lambda h, a: h > a and h + a > 1,
    "1&O2.5": lambda h, a: h > a and h + a > 2,
    "1X&U3.5": lambda h, a: h >= a and h + a < 4,
    "X2&U3.5": lambda h, a: h <= a and h + a < 4,
    "1X&BTTS": lambda h, a: h >= a and h > 0 and a > 0,
    "X2&BTTS": lambda h, a: h <= a and h > 0 and a > 0,
    "1&BTTS": lambda h, a: h > a and a > 0,
    "BTTS&O2.5": lambda h, a: h > 0 and a > 0 and h + a > 2,
}

ACCA_30 = [
    ("como_sassuolo", "1&O1.5"),
    ("arsenal_everton", "1"),
    ("leipzig_elversberg", "1&O1.5"),
    ("koln_schalke", "1X&U3.5"),
    ("paderborn_hsv", "BTTS"),
    ("mainz_werder", "1X"),
    ("cagliari_bologna", "U2.5"),
    ("coventry_fulham", "X2"),
]

ACCA_40 = [
    ("leipzig_elversberg", "1&O2.5"),
    ("como_sassuolo", "1&O1.5"),
    ("arsenal_everton", "1X&U3.5"),
    ("mainz_werder", "BTTS"),
    ("augsburg_union", "1X&BTTS"),
    ("racing_espanyol", "U3.5"),
    ("paderborn_hsv", "BTTS"),
]


def report():
    grids = {k: grid(lh, la) for k, (_, _, lh, la) in MATCHES.items()}
    for key, (home, away, lh, la) in MATCHES.items():
        g = grids[key]
        print(f"\n{home} vs {away}  (xG {lh:.2f}-{la:.2f})")
        print("  " + "  ".join(f"{m}:{prob(g, MARKETS[m]):.0%}"
                               for m in ("1", "X", "2", "O2.5", "BTTS")))
    for name, slip in (("ACCA ~30x", ACCA_30), ("ACCA ~40x", ACCA_40)):
        print(f"\n=== {name} ===")
        odds, probs = [], []
        for key, mkt in slip:
            p = prob(grids[key], MARKETS[mkt])
            o = 1 / p / MARGIN
            odds.append(o)
            probs.append(p)
            print(f"  {MATCHES[key][0]:>16} vs {MATCHES[key][1]:<14} "
                  f"{mkt:<10} p={p:.1%}  est.odd={o:.2f}")
        print(f"  total odds = {prod(odds):.2f}   "
              f"model hit rate = {prod(probs):.2%}")


if __name__ == "__main__":
    report()
