"""Blast Off Billionaire executables - defines game execution flow."""

from game_calculations import GameCalculations


class GameExecutables(GameCalculations):
    """Execution logic for Blast Off Billionaire."""
    
    def execute_spin(self):
        """
        Execute a single spin of Blast Off Billionaire.
        
        Returns:
            dict: Spin outcome data
        """
        return self.calculate_spin_outcome()