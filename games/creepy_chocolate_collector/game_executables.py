from game_calculations import GameCalculations
from src.calculations.lines import Lines
from src.events.events import win_info_event, set_win_event, set_total_event


class GameExecutables(GameCalculations):

    def evaluate_lines_board(self):
        """Populate win-data, record wins, transmit events."""
        # In bonus mode, CW should substitute only (no multiplier applied to line wins)
        # CW multipliers are only used for CC collection, not line wins
        multiplier_method = "global" if self.gametype == self.config.freegame_type else "symbol"
        
        self.win_data = Lines.get_lines(
            self.board, 
            self.config, 
            global_multiplier=self.global_multiplier,
            multiplier_method=multiplier_method
        )
        Lines.record_lines_wins(self)
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        
        # Custom event emission for creepy chocolate collector
        # Skip set_win_event AND set_total_event here - they will be called after collections are processed
        if self.win_manager.spin_win > 0:
            win_info_event(self)
            self.evaluate_wincap()
