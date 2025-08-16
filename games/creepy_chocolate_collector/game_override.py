from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome


class GameStateOverride(GameExecutables):
    """
    This class is is used to override or extend universal state.py functions.
    e.g: A specific game may have custom book properties to reset
    """

    def reset_book(self):
        super().reset_book()
        # Initialize collector wild tracking for multiplier ladder
        if not hasattr(self, 'collectors_collected'):
            self.collectors_collected = 0
        if not hasattr(self, 'current_multiplier_index'):
            self.current_multiplier_index = 0
        
        # Initialize custom statistics tracking
        if not hasattr(self, 'total_chocolate_collected'):
            self.total_chocolate_collected = 0
        if not hasattr(self, 'total_extra_spins_granted'):
            self.total_extra_spins_granted = 0
        if not hasattr(self, 'max_multiplier_reached'):
            self.max_multiplier_reached = 0
        
        # Reset bonus tracking when starting a new game round
        if self.gametype == self.config.basegame_type:
            self.collectors_collected = 0
            self.current_multiplier_index = 0
            self.total_chocolate_collected = 0
            self.total_extra_spins_granted = 0
            self.max_multiplier_reached = 0

    def assign_special_sym_function(self):
        self.special_symbol_functions = {
            "W": [self.assign_mult_property],
            "CW": [self.assign_collector_properties],
            "CC": [self.assign_chocolate_cash_value],
        }

    def assign_mult_property(self, symbol) -> dict:
        """Assign multiplier value to Wild symbol in freegame."""
        multiplier_value = 1
        if self.gametype == self.config.freegame_type:
            multiplier_value = get_random_outcome(
                self.get_current_distribution_conditions()["mult_values"][self.gametype]
            )
        symbol.assign_attribute({"multiplier": multiplier_value})

    def assign_collector_properties(self, symbol) -> dict:
        """Assign properties to Collector Wild symbol in bonus."""
        # Always assign collector property to CW symbols (they only appear in bonus)
        current_multiplier = self.config.collector_multipliers[self.current_multiplier_index]
        symbol.assign_attribute({
            "multiplier": current_multiplier,
            "collector": True
        })
        

    def assign_chocolate_cash_value(self, symbol) -> dict:
        """Assign cash value to Chocolate Cash symbol."""
        cash_value = get_random_outcome(
            self.config.padding_symbol_values["CC"]["cash_value"]
        )
        symbol.assign_attribute({"cash_value": cash_value})

    def process_collector_wilds(self):
        """Handle Collector Wild collection and multiplier ladder progression."""
        
        if self.gametype != self.config.freegame_type:
            return
            
        # Check if already at bonus cap - use win manager's running total
        if self.win_manager.running_bet_win >= self.config.wincap:
            return
            
        # Find all Collector Wilds and Chocolate Cash symbols on the board
        collector_count = 0
        chocolate_cash_total = 0
        cc_count_for_event = 0
        
        for reel_idx, reel in enumerate(self.board):
            for row_idx, symbol in enumerate(reel):
                if symbol.name == "CW":
                    # Count all CW symbols, even without collector attribute
                    if hasattr(symbol, 'collector') and symbol.collector:
                        collector_count += 1
                    else:
                        # Fallback: treat all CW symbols as collectors in freegame
                        collector_count += 1
                elif symbol.name == "CC":
                    if hasattr(symbol, 'cash_value'):
                        chocolate_cash_total += symbol.cash_value
                        cc_count_for_event += 1
                    else:
                        # Fallback: assign default cash value if missing
                        default_value = get_random_outcome(
                            self.config.padding_symbol_values["CC"]["cash_value"]
                        )
                        symbol.assign_attribute({"cash_value": default_value})
                        chocolate_cash_total += default_value
                        cc_count_for_event += 1
        
        # Only collect if both collectors and chocolate cash are present
        if collector_count == 0 or chocolate_cash_total == 0:
            return
            
        # Simplified collection logic: (chocolate_cash_total * bet_amount) * collectors * current_multiplier
        # Debug: Check bounds
        max_index = len(self.config.collector_multipliers) - 1
        if self.current_multiplier_index > max_index:
            print(f"ERROR: multiplier_index={self.current_multiplier_index} > max={max_index}, multipliers={self.config.collector_multipliers}")
            self.current_multiplier_index = max_index
        
        current_multiplier = self.config.collector_multipliers[self.current_multiplier_index]
        uncapped_value = chocolate_cash_total * collector_count * current_multiplier
        collected_value = uncapped_value
        
        # Debug logging
        print(f"DEBUG COLLECTION: CC_total={chocolate_cash_total}, CW_count={collector_count}, multiplier={current_multiplier}")
        print(f"DEBUG COLLECTION: uncapped={uncapped_value}, running_win={self.win_manager.running_bet_win}, wincap={self.config.wincap}")
        
        # Enforce bonus cap using win manager's running total
        if self.win_manager.running_bet_win + collected_value > self.config.wincap:
            collected_value = self.config.wincap - self.win_manager.running_bet_win
            print(f"DEBUG COLLECTION: CAPPED to {collected_value}")
        else:
            print(f"DEBUG COLLECTION: NOT CAPPED, final={collected_value}")
        
        # Add to current spin wins (only if within cap)  
        if collected_value > 0:
            # Use the standard win update method which properly tracks both spin_win and running_bet_win
            self.win_manager.update_spinwin(collected_value)
            # Track total chocolate collected for statistics
            self.total_chocolate_collected += chocolate_cash_total
            
            # Emit collection event for proper logging
            self.book.add_event({
                'type': 'collection',
                'cw_count': collector_count,
                'cc_count': cc_count_for_event,
                'cc_total_value': chocolate_cash_total,
                'level': self.current_multiplier_index + 1,  # Level 1-4, not multiplier value
                'collected_amount': collected_value
            })
        
        # Track collector wilds for multiplier progression
        self.collectors_collected += collector_count
        
        # Check for multiplier ladder progression (every 4 collectors)
        if self.collectors_collected >= 4:
            self.collectors_collected -= 4  # Reset counter
            self.tot_fs += 10  # Add 10 extra spins
            self.total_extra_spins_granted += 10  # Track extra spins granted
            
            # Advance multiplier ladder if not at max
            if self.current_multiplier_index < len(self.config.collector_multipliers) - 1:
                self.current_multiplier_index += 1
                
        # Track the highest multiplier level reached
        if self.current_multiplier_index > self.max_multiplier_reached:
            self.max_multiplier_reached = self.current_multiplier_index


    def check_repeat(self):
        super().check_repeat()
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
                return
            if win_criteria is None and self.final_win == 0:
                self.repeat = True
                return