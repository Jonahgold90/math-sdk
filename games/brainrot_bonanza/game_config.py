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
                4: 10,  # 4+ scatters → 10 free spins
                5: 10,  # 5 scatters → 10 free spins
                6: 10,  # 6 scatters → 10 free spins
                7: 10,  # 7 scatters → 10 free spins
                8: 10,  # 8 scatters → 10 free spins
                9: 10,  # 9 scatters → 10 free spins
                10: 10, # 10 scatters → 10 free spins
                11: 10, # 11 scatters → 10 free spins
                12: 10, # 12 scatters → 10 free spins
                13: 10, # 13 scatters → 10 free spins
                14: 10, # 14 scatters → 10 free spins
                15: 10, # 15 scatters → 10 free spins
                16: 10, # 16 scatters → 10 free spins
                17: 10, # 17 scatters → 10 free spins
                18: 10, # 18 scatters → 10 free spins
                19: 10, # 19 scatters → 10 free spins
                20: 10, # 20 scatters → 10 free spins
                21: 10, # 21 scatters → 10 free spins
                22: 10, # 22 scatters → 10 free spins
                23: 10, # 23 scatters → 10 free spins
                24: 10, # 24 scatters → 10 free spins
                25: 10, # 25 scatters → 10 free spins
                26: 10, # 26 scatters → 10 free spins
                27: 10, # 27 scatters → 10 free spins
                28: 10, # 28 scatters → 10 free spins
                29: 10, # 29 scatters → 10 free spins
                30: 10, # 30 scatters → 10 free spins (entire board)
            },
            self.freegame_type: {
                3: 5,   # 3+ scatters → +5 spins (retrigger)
                4: 5,   # 4 scatters → +5 spins
                5: 5,   # 5 scatters → +5 spins
                6: 5,   # 6 scatters → +5 spins
                7: 5,   # 7 scatters → +5 spins
                8: 5,   # 8 scatters → +5 spins
                9: 5,   # 9 scatters → +5 spins
                10: 5,  # 10 scatters → +5 spins
                11: 5,  # 11 scatters → +5 spins
                12: 5,  # 12 scatters → +5 spins
                13: 5,  # 13 scatters → +5 spins
                14: 5,  # 14 scatters → +5 spins
                15: 5,  # 15 scatters → +5 spins
                16: 5,  # 16 scatters → +5 spins
                17: 5,  # 17 scatters → +5 spins
                18: 5,  # 18 scatters → +5 spins
                19: 5,  # 19 scatters → +5 spins
                20: 5,  # 20 scatters → +5 spins
                21: 5,  # 21 scatters → +5 spins
                22: 5,  # 22 scatters → +5 spins
                23: 5,  # 23 scatters → +5 spins
                24: 5,  # 24 scatters → +5 spins
                25: 5,  # 25 scatters → +5 spins
                26: 5,  # 26 scatters → +5 spins
                27: 5,  # 27 scatters → +5 spins
                28: 5,  # 28 scatters → +5 spins
                29: 5,  # 29 scatters → +5 spins
                30: 5,  # 30 scatters → +5 spins (entire board)
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
                name="ante",
                cost=1.25,
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
