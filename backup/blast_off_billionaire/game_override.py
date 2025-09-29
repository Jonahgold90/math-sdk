"""Blast Off Billionaire overrides - custom game state logic."""

from game_executables import GameExecutables
from game_events import GameEvents


class GameStateOverride(GameExecutables, GameEvents):
    """
    Override base game state functionality for Blast Off Billionaire.
    """

    def reset_book(self):
        """Reset game specific properties for each spin."""
        super().reset_book()
        
    def assign_special_sym_function(self):
        """No special symbols in Blast Off Billionaire."""
        pass
        
    def check_game_repeat(self):
        """
        Check if the game should repeat the spin to meet distribution criteria.
        This integrates with Stake Engine's distribution system.
        """
        if not self.repeat:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True