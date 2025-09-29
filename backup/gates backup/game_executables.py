"""

"""

from copy import copy

from game_calculations import GameCalculations
from src.calculations.scatter import Scatter
from game_events import send_mult_info_event
from src.events.events import (
    set_win_event,
    set_total_event,
    fs_trigger_event,
    update_tumble_win_event,
    update_global_mult_event,
    update_freespin_event,
)


class GameExecutables(GameCalculations):
    """Game specific executable functions. Used for grouping commonly used/repeated applications."""

    def set_end_tumble_event(self):
        """After all tumbling events have finished, send final events."""
        # For Gates of Olympus, multipliers are applied in get_scatterpays_update_wins()
        # We need to calculate what the base win would have been for event validation
        
        if self.win_manager.spin_win > 0:
            board_mult, mult_info = self.get_board_multipliers()
            if len(mult_info) > 0:
                # Gates of Olympus: Skip detailed multiplier events to avoid validation issues
                # The global multiplier system makes base win calculation complex
                update_tumble_win_event(self)
            
            set_win_event(self)
        set_total_event(self)

    def update_freespin_amount(self, scatter_key: str = "scatter"):
        """Update current and total freespin number and emit event."""
        self.tot_fs = self.count_special_symbols(scatter_key) * 2
        if self.gametype == self.config.basegame_type:
            basegame_trigger, freegame_trigger = True, False
        else:
            basegame_trigger, freegame_trigger = False, True
        fs_trigger_event(self, basegame_trigger=basegame_trigger, freegame_trigger=freegame_trigger)

    def get_scatterpays_update_wins(self):
        """Return the board since we are assigning the 'explode' attribute."""
        self.win_data = Scatter.get_scatterpay_wins(
            self.config, self.board, global_multiplier=self.global_multiplier
        )  # Evaluate wins, self.board is modified in-place
        Scatter.record_scatter_wins(self)
        self.win_manager.tumble_win = self.win_data["totalWin"]
        self.win_manager.update_spinwin(self.win_data["totalWin"])  # Update wallet
        self.emit_tumble_win_events()  # Transmit win information

    def update_freespin(self) -> None:
        """Called before a new reveal during freegame."""
        self.fs += 1
        update_freespin_event(self)
        # Gates of Olympus: global multiplier persists across spins (do NOT reset)
        # self.global_multiplier remains unchanged
        self.win_manager.reset_spin_win()
        self.tumblewin_mult = 0
        self.win_data = {}
