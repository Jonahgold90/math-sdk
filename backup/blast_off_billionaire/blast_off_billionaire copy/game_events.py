"""Blast Off Billionaire events - handles game event generation."""

from src.events.events import EventConstants


class GameEvents:
    """Event handling for Blast Off Billionaire."""
    
    def record_multiplier_outcome(self, spin_outcome):
        """
        Record multiplier outcome for statistics tracking.
        
        Args:
            spin_outcome: Dict containing win data and multiplier information
        """
        multiplier = spin_outcome.get("multiplier", 0.0)
        is_win = spin_outcome.get("is_win", False)
        
        # Determine multiplier range for statistics
        multiplier_range = self._get_multiplier_range(multiplier)
        
        if is_win and multiplier > 0:
            # Record winning multiplier with its range
            self.record({
                "symbol": "multiplier",
                "kind": multiplier_range,
                "gametype": self.gametype,
                "multiplier_value": multiplier,
                "win_amount": spin_outcome.get("totalWin", 0.0)
            })
        else:
            # Record losing spin
            self.record({
                "symbol": "loss",
                "kind": "no_multiplier", 
                "gametype": self.gametype,
                "multiplier_value": 0.0,
                "win_amount": 0.0
            })
    
    def _get_multiplier_range(self, multiplier):
        """
        Determine which multiplier range a value falls into.
        
        Args:
            multiplier: The multiplier value
            
        Returns:
            str: Range identifier (e.g., "0-1", "1-2", etc.)
        """
        if multiplier <= 0:
            return "loss"
        elif 0 <= multiplier < 1:
            return "0-1"
        elif 1 <= multiplier < 2:
            return "1-2"
        elif 2 <= multiplier < 5:
            return "2-5"
        elif 5 <= multiplier < 10:
            return "5-10"
        elif 10 <= multiplier < 20:
            return "10-20"
        elif 20 <= multiplier < 50:
            return "20-50"
        elif 50 <= multiplier < 100:
            return "50-100"
        elif 100 <= multiplier < 200:
            return "100-200"
        elif 200 <= multiplier < 500:
            return "200-500"
        elif 500 <= multiplier < 1000:
            return "500-1000"
        elif 1000 <= multiplier < 2000:
            return "1000-2000"
        elif 2000 <= multiplier < 5000:
            return "2000-5000"
        elif multiplier >= 5000:
            return "5000+"
        else:
            return "other"
    
    def create_spin_event(self, spin_outcome, spin_number):
        """
        Create a spin event for the books system.
        
        Args:
            spin_outcome: Dict containing win data and multiplier
            spin_number: Current spin/simulation number
            
        Returns:
            dict: Event data for books
        """
        event_data = {
            "index": len(self.book.events),
            "type": EventConstants.WIN_DATA.value,
            "spinNumber": spin_number,
            "totalWin": int(round(spin_outcome["totalWin"] * 100, 0)),  # Convert to cents
            "multiplier": spin_outcome["multiplier"],
            "isWin": spin_outcome["is_win"]
        }
        
        
        return event_data