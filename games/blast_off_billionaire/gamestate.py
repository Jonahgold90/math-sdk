"""Blast Off Billionaire game state - main simulation controller."""

from game_override import GameStateOverride
from src.events.events import EventConstants


class GameState(GameStateOverride):
    """Handle all game-logic and event updates for Blast Off Billionaire."""

    def run_spin(self, sim):
        """
        Execute a single simulation spin.
        
        Args:
            sim: Simulation number for seeding and tracking
        """
        self.reset_seed(sim)
        self.repeat = True
        
        while self.repeat:
            self.reset_book()
            
            # Execute the spin and get outcome
            spin_outcome = self.execute_spin()
            
            # Record multiplier outcome for statistics
            self.record_multiplier_outcome(spin_outcome)
            
            # Update win manager with total win amount
            self.win_manager.update_spinwin(spin_outcome["totalWin"])
            self.win_manager.update_gametype_wins(self.gametype)
            
            # Create and add event to book
            game_event = self.create_spin_event(spin_outcome, sim + 1)
            self.book.add_event(game_event)
            
            # Check if spin meets distribution criteria
            self.evaluate_finalwin()
            
        # Record wins in the system
        self.imprint_wins()

    def run_freespin(self):
        """No free spins in Blast Off Billionaire."""
        pass