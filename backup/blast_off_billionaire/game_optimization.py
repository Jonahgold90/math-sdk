"""Set conditions/parameters for optimization program for Blast Off Billionaire"""

from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructConditions,
    verify_optimization_input,
)

print("Starting game optimization")
class OptimizationSetup:
    """Blast Off Billionaire specific optimization setup.
    Amends game_config.opt_params, which is required to setup maths configuration file.
    """

    def __init__(self, game_config):
        self.game_config = game_config
        self.game_config.opt_params = {
            "base": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.001, av_win=5000, search_conditions=5000).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "basegame": ConstructConditions(hr=0.55, rtp=0.949, av_win=1.73).return_dict(),  # 55% hit rate, remaining RTP
                },
                "scaling": ConstructScaling(
                    [
                        {
                            "criteria": "basegame",
                            "scale_factor": 2.0,  # Boost low wins to achieve target RTP
                            "win_range": (0, 100),  # 0-1x multiplier range (in cents)
                            "probability": 1.0,
                        },
                        {
                            "criteria": "basegame", 
                            "scale_factor": 1.0,  # Keep medium multipliers balanced
                            "win_range": (100, 500),  # 1-5x multiplier range
                            "probability": 1.0,
                        },
                        {
                            "criteria": "basegame",
                            "scale_factor": 0.8,  # Reduce high multipliers frequency
                            "win_range": (500, 2000),  # 5-20x multiplier range  
                            "probability": 1.0,
                        },
                        {
                            "criteria": "basegame",
                            "scale_factor": 0.5,  # Significantly reduce very high multipliers
                            "win_range": (2000, 5000),  # 20x+ multiplier range
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=3000,  # Reduced for faster optimization
                    num_per_fence=8000,  # Reduced for faster optimization
                    min_m2m=2,  # Minimum multiplier-to-multiplier ratio
                    max_m2m=6,  # Maximum multiplier-to-multiplier ratio
                    pmb_rtp=0.95,  # Overall target RTP
                    sim_trials=3000,  # Number of simulation trials
                    test_spins=[25, 50, 100],  # Test spin counts
                    test_weights=[0.4, 0.4, 0.2],  # Weights for test spins
                    score_type="rtp",  # Optimize for RTP
                ).return_dict(),
            },
        }

        verify_optimization_input(self.game_config, self.game_config.opt_params)