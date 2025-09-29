from game_override import GameStateOverride
from src.calculations.lines import Lines


class GameState(GameStateOverride):
    """Handles game logic and events for a single simulation number/game-round."""

    def run_spin(self, sim):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board()

            # Evaluate wins, update wallet, transmit events
            self.evaluate_lines_board()

            self.win_manager.update_gametype_wins(self.gametype)
            if self.check_fs_condition():
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        
        # Initialize Big-Bass style bonus state at start of free spins
        self.cw_progress = 0
        self.current_level = 1
        self.segment_level = 1
        self.queued_levelups = 0
        self.queued_retrigs = 0
        self.spins_in_segment = 0
        self.current_segment_length = self.tot_fs  # First segment matches initial bonus length
        
        while self.fs < self.tot_fs:
            self.update_freespin()
            self.draw_board()

            self.evaluate_lines_board()
            
            # Handle Collector Wild chocolate cash collection
            self.process_collector_wilds()
                
            # No scatters appear in bonus mode for this game
            # if self.check_fs_condition():
            #     self.update_fs_retrigger_amt()

            self.win_manager.update_gametype_wins(self.gametype)

            # Check if bonus cap reached - end bonus immediately AFTER accounting for wins
            if self.win_manager.running_bet_win >= self.config.wincap:
                break  # Exit the freespin loop immediately

        self.end_freespin()
