from game_override import GameStateOverride
from src.calculations.scatter import Scatter
from game_events import send_multiplier_landed_event


class GameState(GameStateOverride):
    """Gamestate for a single spin"""

    def run_spin(self, sim: int):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board()
            self.get_scatterpays_update_wins()

            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                self.tumble_game_board()
                send_multiplier_landed_event(self)  # Check for new multipliers after tumble
                self.get_scatterpays_update_wins()

            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition() and self.check_freespin_entry():
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        while self.fs < self.tot_fs:
            # Resets global multiplier at each spin
            self.update_freespin()
            self._laser_fired_this_spin = False  # Reset laser flag for new spin
            self.draw_board()
            send_multiplier_landed_event(self)  # Check for multipliers on initial board

            self.get_scatterpays_update_wins()

            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                self.tumble_game_board()
                send_multiplier_landed_event(self)  # Check for new multipliers after tumble
                self.get_scatterpays_update_wins()

            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

        self.end_freespin()
