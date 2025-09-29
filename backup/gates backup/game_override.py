from game_executables import *
from src.events.events import update_freespin_event, update_global_mult_event
from src.calculations.statistics import get_random_outcome


class GameStateOverride(GameExecutables):
    """
    This class is is used to override or extend universal state.py functions.
    e.g: A specific game may have custom book properties to reset
    """

    def reset_book(self):
        # Reset global values used across multiple projects
        super().reset_book()
        # Reset parameters relevant to local game only
        self.tumble_win = 0

    def reset_fs_spin(self):
        super().reset_fs_spin()
        self.global_multiplier = 0  # Gates of Olympus starts at 0, not 1

    def assign_special_sym_function(self):
        self.special_symbol_functions = {"M": [self.assign_mult_property]}

    def assign_mult_property(self, symbol):
        """Use betmode conditions to assign multiplier attribute to multiplier symbol."""
        multiplier_value = get_random_outcome(
            self.get_current_distribution_conditions()["mult_values"][self.gametype]
        )
        symbol.assign_attribute({"multiplier": multiplier_value})

    def get_scatterpays_update_wins(self):
        """Gates of Olympus: Calculate wins and handle global multiplier accumulation."""
        from src.calculations.scatter import Scatter
        
        if self.gametype == self.config.freegame_type:
            # Free spins: Calculate wins with current global multiplier
            self.win_data = Scatter.get_scatterpay_wins(
                self.config, self.board, global_multiplier=max(1, self.global_multiplier)
            )
            
            # If wins occurred and multipliers present, accumulate them
            if self.win_data.get("totalWin", 0) > 0:
                board_mult, mult_info = self.get_board_multipliers()
                if len(mult_info) > 0:
                    multiplier_sum = sum(info["value"] for info in mult_info)
                    self.global_multiplier += multiplier_sum
                    
                    # Recalculate wins with new global multiplier
                    self.win_data = Scatter.get_scatterpay_wins(
                        self.config, self.board, global_multiplier=max(1, self.global_multiplier)
                    )
                    update_global_mult_event(self)
        else:
            # Base game: Normal calculation
            self.win_data = Scatter.get_scatterpay_wins(
                self.config, self.board, global_multiplier=1
            )
        
        Scatter.record_scatter_wins(self)
        self.win_manager.tumble_win = self.win_data["totalWin"]
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        
    def update_global_mult(self):
        """Gates of Olympus: This is now handled in get_scatterpays_update_wins."""
        pass

    def check_game_repeat(self):
        """Verify final win matches required betmode conditions."""
        if self.repeat == False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
