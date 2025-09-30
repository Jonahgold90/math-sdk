import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):
    """Load all game specific parameters and elements"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "brainrot_bonanza"
        self.game_name = "sample_scatter"
        self.provider_numer = 0
        self.working_name = "Sample scatter pay (pay anywhere)"
        self.wincap = 5000.0
        self.win_type = "scatter"
        self.rtp = 0.9600
        self.construct_paths()

        # Game Dimensions
        self.num_reels = 6
        # Optionally include variable number of rows per reel
        self.num_rows = [5] * self.num_reels
        # Board and Symbol Properties
        # Math spec: 8-9, 10-11, 12+ symbols
        t1, t2, t3 = (8, 9), (10, 11), (12, 30)
        pay_group = {
            # High pays (h1-h4)
            (t1, "H1"): 10.00,   # 8-9 symbols
            (t2, "H1"): 25.00,   # 10-11 symbols
            (t3, "H1"): 50.00,   # 12+ symbols
            (t1, "H2"): 2.50,
            (t2, "H2"): 10.00,
            (t3, "H2"): 25.00,
            (t1, "H3"): 2.00,
            (t2, "H3"): 5.00,
            (t3, "H3"): 15.00,
            (t1, "H4"): 1.50,
            (t2, "H4"): 2.00,
            (t3, "H4"): 12.00,
            # Low pays (l1-l5)
            (t1, "L1"): 1.00,
            (t2, "L1"): 1.50,
            (t3, "L1"): 10.00,
            (t1, "L2"): 0.80,
            (t2, "L2"): 1.00,
            (t3, "L2"): 8.00,
            (t1, "L3"): 0.50,
            (t2, "L3"): 1.00,
            (t3, "L3"): 5.00,
            (t1, "L4"): 0.40,
            (t2, "L4"): 0.90,
            (t3, "L4"): 4.00,
            # Scatter pays
            # ((4, 4), "S"): 3.00,
            # ((5, 5), "S"): 5.00,
            # ((6, 30), "S"): 100.00,
        }
        self.paytable = self.convert_range_table(pay_group)

        self.include_padding = True
        self.special_symbols = {"wild": ["W"],
                                "scatter": ["S"], "multiplier": ["M"]}

        self.freespin_triggers = {
            self.basegame_type: {
                3: 8,
                4: 12,
                5: 15,
                6: 17,
                7: 19,
                8: 21,
                9: 23,
                10: 24,
            },
            self.freegame_type: {
                2: 3,
                3: 5,
                4: 8,
                5: 12,
                6: 14,
                7: 16,
                8: 18,
                9: 10,
                10: 12,
            },
        }
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }
        # Reels
        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(
                os.path.join(self.reels_path, f))

        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]
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
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "mult_values": {
                                self.basegame_type: {},  # No multipliers in base game
                                self.freegame_type: {
                                    100: 1,    # All high multipliers for wincap forcing
                                    200: 1,
                                    300: 1,
                                    400: 1,
                                    500: 1,
                                    1000: 1
                                },
                            },
                            "scatter_triggers": {4: 1, 5: 2},
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.1,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {4: 5, 5: 1},
                            "mult_values": {
                                self.basegame_type: {},  # No multipliers in base game
                                self.freegame_type: {
                                    2: 100,    # ~22% chance
                                    3: 80,     # ~18% chance
                                    4: 70,     # ~15% chance
                                    5: 50,     # ~11% chance
                                    6: 40,     # ~9% chance
                                    8: 30,     # ~7% chance
                                    10: 25,    # ~5.5% chance
                                    12: 20,    # ~4.4% chance
                                    15: 15,    # ~3.3% chance
                                    20: 10,    # ~2.2% chance
                                    25: 8,     # ~1.8% chance
                                    50: 5,     # ~1.1% chance
                                    100: 2,    # ~0.4% chance
                                    1000: 1    # ~0.2% chance
                                },
                            },
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.4,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "mult_values": {
                                self.basegame_type: {},  # No multipliers in base game
                                self.freegame_type: {
                                    2: 100,    # ~22% chance
                                    3: 80,     # ~18% chance
                                    4: 70,     # ~15% chance
                                    5: 50,     # ~11% chance
                                    6: 40,     # ~9% chance
                                    8: 30,     # ~7% chance
                                    10: 25,    # ~5.5% chance
                                    12: 20,    # ~4.4% chance
                                    15: 15,    # ~3.3% chance
                                    20: 10,    # ~2.2% chance
                                    25: 8,     # ~1.8% chance
                                    50: 5,     # ~1.1% chance
                                    100: 2,    # ~0.4% chance
                                    1000: 1    # ~0.2% chance
                                },
                            },
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.5,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "mult_values": {
                                self.basegame_type: {},  # No multipliers in base game
                                self.freegame_type: {
                                    2: 1000,   # Very common
                                    3: 500,    # Common
                                    4: 300,    # Common
                                    5: 200,    # Uncommon
                                    6: 150,    # Uncommon
                                    8: 100,    # Rare
                                    10: 80,    # Rare
                                    12: 60,    # Rare
                                    15: 40,    # Very rare
                                    20: 20,    # Very rare
                                    25: 10,    # Very rare
                                    50: 5,     # Extremely rare
                                    100: 2,    # Extremely rare
                                    1000: 1    # Extremely rare
                                }
                            },
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
            BetMode(
                name="bonus",
                cost=100.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "mult_values": {
                                self.basegame_type: {},  # No multipliers in base game
                                self.freegame_type: {
                                    100: 1,    # All high multipliers for wincap forcing
                                    200: 1,
                                    300: 1,
                                    400: 1,
                                    500: 1,
                                    1000: 1
                                },
                            },
                            "scatter_triggers": {4: 10, 5: 5, 6: 1},
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.1,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {4: 10, 5: 5, 6: 1},
                            "mult_values": {
                                self.basegame_type: {},  # No multipliers in base game
                                self.freegame_type: {
                                    2: 100,    # ~22% chance
                                    3: 80,     # ~18% chance
                                    4: 70,     # ~15% chance
                                    5: 50,     # ~11% chance
                                    6: 40,     # ~9% chance
                                    8: 30,     # ~7% chance
                                    10: 25,    # ~5.5% chance
                                    12: 20,    # ~4.4% chance
                                    15: 15,    # ~3.3% chance
                                    20: 10,    # ~2.2% chance
                                    25: 8,     # ~1.8% chance
                                    50: 5,     # ~1.1% chance
                                    100: 2,    # ~0.4% chance
                                    1000: 1    # ~0.2% chance
                                },
                            },
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                ],
            ),
        ]
