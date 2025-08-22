from game_calculations import GameCalculations
from src.calculations.lines import Lines


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
        Lines.emit_linewin_events(self)
