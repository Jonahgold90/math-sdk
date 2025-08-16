from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome


class GameStateOverride(GameExecutables):
    """
    This class is is used to override or extend universal state.py functions.
    e.g: A specific game may have custom book properties to reset
    """

    def reset_book(self):
        super().reset_book()
        # Initialize collector wild tracking for Big-Bass style multiplier ladder
        if not hasattr(self, 'cw_progress'):
            self.cw_progress = 0  # Total CWs collected (all CWs count)
        if not hasattr(self, 'current_level'):
            self.current_level = 1  # Current level (1-4)
        if not hasattr(self, 'segment_level'):
            self.segment_level = 1  # Locked level for current 10-spin segment
        if not hasattr(self, 'queued_levelups'):
            self.queued_levelups = 0  # Number of pending level-ups
        if not hasattr(self, 'spins_in_segment'):
            self.spins_in_segment = 0  # Current spin within 10-spin segment
        
        # Initialize custom statistics tracking
        if not hasattr(self, 'total_chocolate_collected'):
            self.total_chocolate_collected = 0
        if not hasattr(self, 'total_extra_spins_granted'):
            self.total_extra_spins_granted = 0
        if not hasattr(self, 'max_multiplier_reached'):
            self.max_multiplier_reached = 0
        
        # Reset bonus tracking when starting a new game round
        if self.gametype == self.config.basegame_type:
            self.cw_progress = 0
            self.current_level = 1
            self.segment_level = 1
            self.queued_levelups = 0
            self.spins_in_segment = 0
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
        # Use segment-locked level for multiplier
        segment_multiplier = self.config.collector_multipliers[self.segment_level - 1]
        symbol.assign_attribute({
            "multiplier": segment_multiplier,
            "collector": True
        })
        

    def assign_chocolate_cash_value(self, symbol) -> dict:
        """Assign cash value to Chocolate Cash symbol."""
        cash_value = get_random_outcome(
            self.config.padding_symbol_values["CC"]["cash_value"]
        )
        symbol.assign_attribute({"cash_value": cash_value})

    def process_collector_wilds(self):
        """Handle Big-Bass style Collector Wild collection and level progression."""
        
        if self.gametype != self.config.freegame_type:
            #print(f"DEBUG: Skipping process_collector_wilds - gametype={self.gametype}, freegame_type={self.config.freegame_type}")
            return
            
        # Check if already at bonus cap
        if self.win_manager.running_bet_win >= self.config.wincap:
            return
            
        # Find all Collector Wilds and Chocolate Cash symbols on the board
        cw_count_this_spin = 0
        chocolate_cash_total = 0
        cc_count_for_event = 0
        cc_values = []
        
        for reel_idx, reel in enumerate(self.board):
            for row_idx, symbol in enumerate(reel):
                if symbol.name == "CW":
                    # ALL CWs count for progression (Big-Bass style)
                    cw_count_this_spin += 1
                elif symbol.name == "CC":
                    if hasattr(symbol, 'cash_value'):
                        chocolate_cash_total += symbol.cash_value
                        cc_count_for_event += 1
                        cc_values.append(symbol.cash_value)
                    else:
                        # Fallback: assign default cash value if missing
                        default_value = get_random_outcome(
                            self.config.padding_symbol_values["CC"]["cash_value"]
                        )
                        symbol.assign_attribute({"cash_value": default_value})
                        chocolate_cash_total += default_value
                        cc_count_for_event += 1
                        cc_values.append(default_value)
        
        # Track ALL CWs for progression (whether they collect or not)
        if cw_count_this_spin > 0:
            self.cw_progress += cw_count_this_spin
            
            # Check for level-up triggers (every 4 CWs)
            while self.cw_progress >= 4:
                self.cw_progress -= 4  # Reset counter
                self.tot_fs += 10  # Add 10 extra spins (retrigger)
                self.total_extra_spins_granted += 10
                
                # Queue level-up only if it won't exceed Level 4
                if self.current_level + self.queued_levelups < 4:
                    self.queued_levelups += 1
                    #print(f"DEBUG: Level-up queued! Current level: {self.current_level}, Queued: {self.queued_levelups}")
        
        # Collection logic (only if both CW and CC present)
        collected_value = 0
        if cw_count_this_spin > 0 and chocolate_cash_total > 0:
            # Use SEGMENT-LOCKED multiplier
            segment_multiplier = self.config.collector_multipliers[self.segment_level - 1]
            uncapped_value = chocolate_cash_total * cw_count_this_spin * segment_multiplier
            collected_value = uncapped_value
            
            # Debug logging
            #print(f"DEBUG COLLECTION: CC_sum={chocolate_cash_total}, CW_count={cw_count_this_spin}, segment_level={self.segment_level}, multiplier={segment_multiplier}")
            #print(f"DEBUG COLLECTION: uncapped={uncapped_value}, running_win={self.win_manager.running_bet_win}, wincap={self.config.wincap}")
            
            # Enforce bonus cap using win manager's running total
            if self.win_manager.running_bet_win + collected_value > self.config.wincap:
                collected_value = self.config.wincap - self.win_manager.running_bet_win
                #print(f"DEBUG COLLECTION: CAPPED to {collected_value}")
            # else:
            #     #print(f"DEBUG COLLECTION: NOT CAPPED, final={collected_value}")
            
            # Add to current spin wins (only if within cap)  
            if collected_value > 0:
                # Use the standard win update method which properly tracks both spin_win and running_bet_win
                self.win_manager.update_spinwin(collected_value)
                # Track total chocolate collected for statistics
                self.total_chocolate_collected += chocolate_cash_total
                
                # Calculate per-CW payouts with proper remainder handling
                payout_per_cw_raw = chocolate_cash_total * segment_multiplier
                base = collected_value // cw_count_this_spin
                rem = int(collected_value - base * cw_count_this_spin)
                subcollections = []
                for i in range(cw_count_this_spin):
                    amt = base + (1 if i < rem else 0)
                    subcollections.append({'cw_index': i, 'amount': amt})
                
                # Emit collection event for proper logging
                self.book.add_event({
                    'type': 'collection',
                    'spin': self.fs + 1,  # Current spin number
                    'level': self.segment_level,  # Segment-locked level
                    'cw_count': cw_count_this_spin,
                    'cc_count': cc_count_for_event,
                    'cc_values': cc_values,
                    'cc_sum': chocolate_cash_total,
                    'collected_amount': collected_value,
                    'payout_per_cw_raw': payout_per_cw_raw,
                    'subcollections': subcollections
                })
                
        # Track the highest level reached
        max_level_reached = max(self.current_level, self.segment_level)
        if max_level_reached > self.max_multiplier_reached:
            self.max_multiplier_reached = max_level_reached
            
        # DEBUG PROGRESSION
        #print(f"DEBUG PROGRESSION: CW_progress={self.cw_progress}, current_level={self.current_level}, queued_levelups={self.queued_levelups}")
        
        # End-of-spin segment accounting
        self.spins_in_segment += 1
        if self.spins_in_segment >= 10:
            self.spins_in_segment = 0
            # Consume at most one queued level-up per segment
            if self.queued_levelups > 0 and self.current_level < 4:
                self.current_level += 1
                self.queued_levelups -= 1
                self.book.add_event({
                    'type': 'level_advance', 
                    'spin': self.fs + 1, 
                    'new_level': self.current_level
                })
                #print(f"DEBUG: Level advanced to {self.current_level} at segment boundary")
            # Lock the new segment's level
            self.segment_level = self.current_level
            #print(f"DEBUG: New segment started at level {self.segment_level}")


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