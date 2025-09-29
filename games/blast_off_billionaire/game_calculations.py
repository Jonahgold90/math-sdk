"""Blast Off Billionaire calculations - handles multiplier selection logic.

This version enforces payout/multiplier quantization to 0.10 increments so that
event files and LUT CSVs agree with the RGS verification rule:
    payout % 10 == 0   (with bet=1.0 → multiplier increments of 0.10)

- Quantization uses banker-safe rounding (ROUND_HALF_UP) via Decimal.
- Quantization happens AFTER server cap / forced wincap and BEFORE writing outputs.
- Classification uses the QUANTIZED multiplier to avoid boundary mismatches.
"""

import random
from decimal import Decimal, ROUND_HALF_UP

from src.calculations.statistics import get_random_outcome
from src.executables.executables import Executables


# ---------- Quantization helpers ----------

def q_step(x: float, step: float) -> float:
    """Round x to the nearest multiple of `step` using HALF_UP (banker-safe)."""
    q = Decimal(str(step))
    return float((Decimal(str(x)) / q).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * q)

def q10c(x: float) -> float:
    """Quantize to 0.10 increments (10 cents). With bet=1.0, multiplier steps = 0.10."""
    return q_step(x, 0.10)


class GameCalculations(Executables):
    """Handle multiplier calculations for Blast Off Billionaire."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Deterministic RNG for math (seed comes from config or defaults to 42)
        seed = getattr(self.config, "seed", 42)
        self.rng = random.Random(seed)

    # ---------- Sampling utilities ----------

    def get_weighted_multiplier(self, multiplier_ranges: dict) -> float:
        """
        Select a random multiplier from weighted ranges (uniform within the chosen range).

        Args:
            multiplier_ranges: Dict[str, {"min": float, "max": float, "weight": float}]

        Returns:
            float: Selected multiplier value (UNCAPPED & UNQUANTIZED).
        """
        if not multiplier_ranges:
            return 0.0

        choices, weights = [], []
        for _, cfg in multiplier_ranges.items():
            w = float(cfg.get("weight", 0.0))
            if w > 0:
                choices.append(cfg)
                weights.append(w)

        if not choices:
            return 0.0

        selected_range = self.rng.choices(choices, weights=weights, k=1)[0]
        return self.rng.uniform(selected_range["min"], selected_range["max"])

    def _classify_kind(self, multiplier: float, multiplier_ranges: dict):
        """
        Find the range name whose [min, max) contains `multiplier`.
        Inclusive of the last bucket's max to avoid off-by-epsilon misses.
        """
        last_name = None
        last_cfg = None
        for name, cfg in multiplier_ranges.items():
            a, b = cfg["min"], cfg["max"]
            if a <= multiplier < b:
                return name
            last_name, last_cfg = name, cfg

        # Edge case: multiplier == max of the last bucket (e.g., exactly 5000.0)
        if last_name and abs(multiplier - last_cfg["max"]) <= 1e-9:
            return last_name
        return None

    # ---------- Main spin evaluation ----------

    def calculate_spin_outcome(self):
        """
        Calculate the outcome of a single spin.

        Returns:
            dict: {
                "totalWin": float,
                "multiplier": float,
                "is_win": bool,
                "kind": str  # "loss", "wincap", "bonus_wincap", or one of the multiplier range keys
            }
        """
        conditions = self.get_current_distribution_conditions()
        current_criteria = self.get_current_betmode_distributions().get_criteria()
        current_betmode = self.get_current_betmode()

        # Pure loss branch: never sample a multiplier (base mode only)
        if current_criteria == "0":
            return {"totalWin": 0.0, "multiplier": 0.0, "is_win": False, "kind": "loss"}

        # Get bet cost from current bet mode
        bet = current_betmode.get_cost()
        wincap_mult = float(self.config.wincap)

        # Get multiplier ranges from conditions
        multiplier_ranges = conditions.get("multiplier_weights", {})

        # Generate raw multiplier
        raw_multiplier = self.get_weighted_multiplier(multiplier_ranges)

        # Apply hard cap ALWAYS (server truth)
        multiplier = min(raw_multiplier, wincap_mult)

        # If this branch is a forced wincap event, snap exactly to wincap
        if conditions.get("force_wincap", False):
            multiplier = wincap_mult

        # ---- Quantize AFTER cap/forcing so events and LUT align with test rules ----
        multiplier = q10c(multiplier)
        total_win = q10c(multiplier * bet)

        # Classify kind using the QUANTIZED multiplier (so boundaries match LUT)
        kind = self._classify_kind(multiplier, multiplier_ranges)
        if conditions.get("force_wincap", False):
            kind = "wincap"

        return {
            "totalWin": total_win,
            "multiplier": multiplier,
            "is_win": total_win > 0.0,
            "kind": kind,
        }
