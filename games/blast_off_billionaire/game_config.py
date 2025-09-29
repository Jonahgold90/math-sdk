"""
Blast Off Billionaire game configuration - multiplier-based crash game (no reels).

This version:
- Uses a multi-bucket RTP retargeter (can move probability across adjacent tiers)
- Prints analytic RTP after retarget so you can sanity-check before sims
- Stubs a 1x1 board so shared state code doesn't crash (no reels in this game)
"""

from math import isclose
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.config import BetMode


# ---------------------------------------------------------------------------
# RTP helpers
# ---------------------------------------------------------------------------

def analytic_rtp(weights: dict, base_q: float, wincap_q: float, wincap_value: float = 5000.0) -> float:
    """Analytic RTP given buckets (uniform in each bucket), quotas, and wincap value."""
    W = sum(v["weight"] for v in weights.values())
    if W <= 0:
        return 0.0
    mean = lambda k: 0.5 * (weights[k]["min"] + weights[k]["max"])
    EV_base = sum((v["weight"] / W) * mean(k) for k, v in weights.items())
    return base_q * EV_base + wincap_q * float(wincap_value)  # loss_q contributes 0


def retarget_rtp_multi(
    weights: dict,
    base_q: float,
    wincap_q: float,
    target_rtp: float,
    wincap_value: float = 5000.0,
    pairs: list[tuple[str, str]] | None = None,
    locked: set[str] | None = None,
) -> dict:
    """
    Adjust probabilities across adjacent bucket pairs so that:
      base_q * EV_base + wincap_q * wincap_value ≈ target_rtp
    EV_base uses uniform-in-bucket means.

    - If `pairs` is None, use the full adjacent ladder in natural order.
    - `locked` buckets will not change.
    - Preserves total weight exactly (integer weights).
    - Ensures every range gets some hits and becomes consecutively rarer.
    """
    keys = list(weights.keys())
    W = sum(float(weights[k]["weight"]) for k in keys)
    if W <= 0:
        return weights
    locked = set() if locked is None else set(locked)

    # Define order for consecutive rarity (low to high multipliers)
    ordered_keys = [
        "0-1", "1-2", "2-5", "5-10", "10-20",
        "20-50", "50-100", "100-200", "200-500",
        "500-1000", "1000-2000", "2000-5000"
    ]
    # Filter to only include keys that exist in weights
    ordered_keys = [k for k in ordered_keys if k in keys]

    # Probabilities within base
    q = {k: float(weights[k]["weight"]) / W for k in keys}

    def mean(k: str) -> float:
        return 0.5 * (float(weights[k]["min"]) + float(weights[k]["max"]))

    # Minimum weights to ensure hits - back to working values
    min_weights = {
        "0-1": 1000,      # Most frequent
        "1-2": 500,       
        "2-5": 300,       
        "5-10": 150,      
        "10-20": 80,      
        "20-50": 50,      
        "50-100": 30,     
        "100-200": 20,    # Ensure this gets hits
        "200-500": 15,    
        "500-1000": 10,   
        "1000-2000": 5,   
        "2000-5000": 3,   
    }

    # Ensure minimum weights
    for k in keys:
        min_w = min_weights.get(k, 1)
        if weights[k]["weight"] < min_w:
            weights[k]["weight"] = min_w
            
    # Recalculate total and probabilities after minimum adjustment
    W = sum(float(weights[k]["weight"]) for k in keys)
    q = {k: float(weights[k]["weight"]) / W for k in keys}

    # Target EV for base portion
    EV_base = sum(q[k] * mean(k) for k in keys)
    EV_target = (target_rtp - wincap_q * float(wincap_value)) / float(base_q)

    # Only do rebalancing if EV is not close to target
    if not isclose(EV_base, EV_target, abs_tol=1e-12):
        # Default to full adjacent ladder
        if pairs is None:
            order = [
                "0-1", "1-2", "2-5", "5-10", "10-20",
                "20-50", "50-100", "100-200", "200-500",
                "500-1000", "1000-2000", "2000-5000"
            ]
            # define neighbor pairs (low, high); we'll choose direction per rem sign later
            pairs = [(order[i], order[i + 1]) for i in range(len(order) - 1)]

        rem = EV_base - EV_target  # >0 -> need to LOWER EV, <0 -> need to RAISE EV

        # Iterate until we converge or cannot move more mass
        while abs(rem) > 1e-12:
            progressed = False
            for low, high in pairs:
                if low not in q or high not in q or low in locked or high in locked:
                    continue
                ml, mh = mean(low), mean(high)

                if rem > 0:
                    # Lower EV: move mass from higher-mean -> lower-mean
                    donor, recv = (high, low) if mh >= ml else (low, high)
                    m_d, m_r = (mh, ml) if mh >= ml else (ml, mh)
                else:
                    # Raise EV: move mass from lower-mean -> higher-mean
                    donor, recv = (low, high) if ml <= mh else (high, low)
                    m_d, m_r = (ml, mh) if ml <= mh else (mh, ml)

                gap = abs(m_d - m_r)
                if gap <= 0:
                    continue

                delta_needed = abs(rem) / gap
                available = q[donor]
                if available <= 0:
                    continue

                delta = min(delta_needed, available)
                if delta <= 0:
                    continue

                # Apply transfer
                q[donor] -= delta
                q[recv] += delta

                change = delta * gap
                rem = rem - (change if rem > 0 else -change)
                progressed = True

                if abs(rem) <= 1e-12:
                    break

            if not progressed:
                # Cannot move further with provided pairs/locks
                break

    # Re-inflate to integers and preserve exact total
    float_w = {k: max(0.0, q[k] * W) for k in keys}
    rounded = {k: int(round(v)) for k, v in float_w.items()}
    
    # Enforce minimum weights
    for k in keys:
        min_w = min_weights.get(k, 1)
        rounded[k] = max(rounded[k], min_w)
    
    diff = int(round(W)) - sum(rounded.values())
    if diff != 0:
        rema = {k: float_w[k] - rounded[k] for k in keys}
        order = sorted(keys, key=lambda k: rema[k], reverse=(diff > 0))
        for k in order:
            if diff == 0:
                break
            min_w = min_weights.get(k, 1)
            nv = rounded[k] + (1 if diff > 0 else -1)
            if nv >= min_w:  # Respect minimums
                rounded[k] = nv
                diff += (-1 if diff > 0 else 1)

    return {k: {"min": weights[k]["min"], "max": weights[k]["max"], "weight": max(min_weights.get(k, 1), rounded[k])} for k in keys}


# ---------------------------------------------------------------------------
# Game config
# ---------------------------------------------------------------------------

class GameConfig(Config):
    """Blast Off Billionaire configuration class."""

    def __init__(self):
        super().__init__()
        self.game_id = "blast_off_billionaire"
        self.provider_number = 1
        self.working_name = "Blast Off Billionaire"
        self.wincap = 5000
        self.win_type = "other"
        self.rtp = 0.95
        self.seed = 42  # used by GameCalculations RNG

        self.construct_paths()

        # Minimal board geometry to satisfy shared state code
        self.num_reels = 1
        self.num_rows = [1]
        self.paytable = {}
        self.include_padding = False
        self.special_symbols = {"wild": [], "scatter": [], "multiplier": []}

        # No free spins in base game
        self.freespin_triggers = {self.basegame_type: {}, self.freegame_type: {}}
        self.anticipation_triggers = {self.basegame_type: 0, self.freegame_type: 0}

        # Manual weights drastically reduced to target ~0.94-0.95 RTP with loss_q=0.60
        self.multiplier_ranges = {
            "0-1":       {"min": 0.01,  "max": 1.0,    "weight": 3920},  # was 3744 → −3%
            "1-2":       {"min": 1.0,   "max": 2.0,    "weight": 1400},   # was 810  → +5%
            "2-5":       {"min": 2.0,   "max": 5.0,    "weight": 381},   # was 363  → +5%

            "5-10":      {"min": 5.0,   "max": 10.0,   "weight": 172},   # =
            "10-20":     {"min": 10.0,  "max": 20.0,   "weight": 58},    # =
            "20-50":     {"min": 20.0,  "max": 50.0,   "weight": 12},    # =

            "50-100":    {"min": 50.0,  "max": 100.0,  "weight": 3},     # =
            "100-200":   {"min": 100.0, "max": 200.0,  "weight": 2},     # floor present
            "200-500":   {"min": 200.0, "max": 500.0,  "weight": 1},     # floor
            "500-1000":  {"min": 500.0, "max": 1000.0, "weight": 1},     # floor
            "1000-2000": {"min": 1000.0,"max": 2000.0, "weight": 1.5},     # was 0/1 → set to 2 (fills gap)
            "2000-5000": {"min": 2000.0,"max": 5000.0, "weight": 1},     # floor
        }



        # Quotas used in BetMode distributions
        # Adjusted quotas to support 0.95 RTP target with new weight distribution
        loss_q   = 0.55 #0 win - increased significantly to reduce RTP
        wincap_q = 0.00001  # reduced wincap frequency
        base_q   = 1.0 - loss_q - wincap_q  

        # ---- Skip retargeting - use raw weights ----
        # Just calculate and display what RTP we get with the raw weights
        raw_rtp = analytic_rtp(self.multiplier_ranges, base_q, wincap_q, self.wincap)
        print(f"Raw RTP (no retargeting): {raw_rtp:.6f} (target: {self.rtp:.6f})")


        # Bet mode setup - only base mode
        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    # Pure losses (no multiplier sampling)
                    Distribution(
                        criteria="0",
                        quota=loss_q,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {},
                            "multiplier_weights": {},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    # Forced wincap hits (exact 5000x)
                    Distribution(
                        criteria="wincap",
                        quota=wincap_q,
                        win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {},
                            "multiplier_weights": self.multiplier_ranges,
                            "force_wincap": True,
                            "force_freegame": False,
                        },
                    ),
                    # Basegame multipliers (use weights; server caps will still apply)
                    Distribution(
                        criteria="basegame",
                        quota=base_q,
                        conditions={
                            "reel_weights": {},
                            "multiplier_weights": self.multiplier_ranges,
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            )
        ]
