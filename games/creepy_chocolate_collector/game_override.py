from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome
from src.events.events import spin_win_total_event, cc_collect_sequence_event, cw_landed_event


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
        if not hasattr(self, 'queued_retrigs'):
            self.queued_retrigs = 0  # Number of pending retrigs (10 spins each)
        if not hasattr(self, 'spins_in_segment'):
            self.spins_in_segment = 0  # Current spin within current segment
        if not hasattr(self, 'current_segment_length'):
            self.current_segment_length = 10  # Length of current segment (first = initial bonus, rest = 10)
        
        # Initialize spin-level win tracking for spinWinTotal event
        self.spin_line_wins = 0  # Line wins for current spin
        self.spin_collections = 0  # Collections for current spin
        
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
            self.queued_retrigs = 0
            self.spins_in_segment = 0
            self.current_segment_length = 10
            self.total_chocolate_collected = 0
            self.total_extra_spins_granted = 0
            self.max_multiplier_reached = 0

    def evaluate_lines_board(self):
        """Override to capture line wins for spinWinTotal event."""
        # Reset spin-level tracking at start of each spin
        self.spin_line_wins = 0
        self.spin_collections = 0
        
        # Call parent implementation
        super().evaluate_lines_board()
        
        # Capture line wins for this spin
        self.spin_line_wins = self.win_data["totalWin"]

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
        cw_positions = []
        cc_positions = []
        cw_count_this_spin = 0
        chocolate_cash_total = 0
        cc_count_for_event = 0
        cc_values = []
        
        for reel_idx, reel in enumerate(self.board):
            for row_idx, symbol in enumerate(reel):
                if symbol.name == "CW":
                    # ALL CWs count for progression (Big-Bass style)
                    cw_count_this_spin += 1
                    # Store CW position and level info for sequencing
                    segment_multiplier = self.config.collector_multipliers[self.segment_level - 1]
                    cw_positions.append({
                        "col": reel_idx,
                        "row": row_idx,
                        "level": self.segment_level,
                        "multiplier": segment_multiplier
                    })
                elif symbol.name == "CC":
                    if hasattr(symbol, 'cash_value'):
                        chocolate_cash_total += symbol.cash_value
                        cc_count_for_event += 1
                        cc_values.append(symbol.cash_value)
                        cc_positions.append({
                            "col": reel_idx,
                            "row": row_idx,
                            "cash_value": symbol.cash_value
                        })
                    else:
                        # Fallback: assign default cash value if missing
                        default_value = get_random_outcome(
                            self.config.padding_symbol_values["CC"]["cash_value"]
                        )
                        symbol.assign_attribute({"cash_value": default_value})
                        chocolate_cash_total += default_value
                        cc_count_for_event += 1
                        cc_values.append(default_value)
                        cc_positions.append({
                            "col": reel_idx,
                            "row": row_idx,
                            "cash_value": default_value
                        })
        
        # Track ALL CWs for progression (whether they collect or not)
        if cw_count_this_spin > 0:
            # Emit cwLanded event after reels stop, before win animations start
            # Calculate total CWs (this spin + previous progress)
            total_cws_accumulated = self.cw_progress + cw_count_this_spin
            cw_landed_event(self, cw_count_this_spin, total_cws_accumulated)
            
            self.cw_progress += cw_count_this_spin
            
            # Check for level-up triggers (every 4 CWs)
            while self.cw_progress >= 4:
                self.cw_progress -= 4  # Reset counter
                
                # Only queue retrigs if we haven't reached level 4 yet
                # Maximum 3 retrigs: 1 for level 2, 1 for level 3, 1 for level 4
                if self.current_level + self.queued_levelups < 4:
                    self.queued_levelups += 1
                    self.queued_retrigs += 1  # Queue the retrig for segment boundary
                    #print(f"DEBUG: Level-up and retrig queued! Current level: {self.current_level}, Queued levelups: {self.queued_levelups}, Queued retrigs: {self.queued_retrigs}")
                else:
                    # At level 4, no more retrigs allowed
                    #print(f"DEBUG: Max level reached, no retrig granted")
                    pass
        
        # Collection logic (only if both CW and CC present)
        collected_value = 0
        collections_sequence = []
        
        if cw_count_this_spin > 0 and chocolate_cash_total > 0:
            # Sort CC positions deterministically: left-to-right, top-to-bottom
            cc_positions_sorted = sorted(cc_positions, key=lambda cc: (cc["col"], cc["row"]))
            
            # Build deterministic collection sequence (non-proportional)
            # Each CW collects every CC independently with full credit
            total_collection_value = 0
            
            for cw_idx, cw_pos in enumerate(cw_positions):
                cw_steps = []
                cw_total = 0
                
                # Each CW collects every CC on the board with full multiplier
                for cc_pos in cc_positions_sorted:
                    base_value = cc_pos["cash_value"]
                    multiplier_used = cw_pos["multiplier"]
                    credited_value = base_value * multiplier_used
                    cw_total += credited_value
                    
                    cw_steps.append({
                        "cc": {"col": cc_pos["col"], "row": cc_pos["row"]},
                        "base_value": base_value,
                        "multiplier_used": multiplier_used,
                        "credited_value": credited_value
                    })
                
                collections_sequence.append({
                    "cw": {"col": cw_pos["col"], "row": cw_pos["row"]},
                    "cw_level": cw_pos["level"],
                    "cw_multiplier": cw_pos["multiplier"],
                    "steps": cw_steps,
                    "total": cw_total
                })
                
                # Add this CW's total to overall collection
                total_collection_value += cw_total
            
            # Use the calculated total collection value
            collected_value = total_collection_value
            
            # Debug logging
            #print(f"DEBUG COLLECTION: CC_sum={chocolate_cash_total}, CW_count={cw_count_this_spin}, segment_level={self.segment_level}")
            #print(f"DEBUG COLLECTION: uncapped={collected_value}, running_win={self.win_manager.running_bet_win}, wincap={self.config.wincap}")
            
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
                # Track collections for this spin
                self.spin_collections += collected_value
                
                # Calculate per-CW payouts for legacy event (proportional to their contribution)
                payout_per_cw_raw = chocolate_cash_total * self.config.collector_multipliers[self.segment_level - 1]
                base = collected_value // cw_count_this_spin if cw_count_this_spin > 0 else 0
                rem = int(collected_value - base * cw_count_this_spin) if cw_count_this_spin > 0 else 0
                subcollections = []
                for i in range(cw_count_this_spin):
                    amt = base + (1 if i < rem else 0)
                    subcollections.append({'cw_index': i, 'amount': amt})
                
                # Emit deterministic collection sequence event
                if collections_sequence:
                    cc_collect_sequence_event(self, collections_sequence)
                
                # Emit original collection event for proper logging
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
        if self.spins_in_segment >= self.current_segment_length:
            self.spins_in_segment = 0
            
            # Process level-up and retrig together
            spins_granted = 0
            if self.queued_retrigs > 0:
                spins_granted = self.queued_retrigs * 10
                self.tot_fs += spins_granted
                self.total_extra_spins_granted += spins_granted
                self.queued_retrigs = 0
            
            # Consume at most one queued level-up per segment
            if self.queued_levelups > 0 and self.current_level < 4:
                self.current_level += 1
                self.queued_levelups -= 1
                self.book.add_event({
                    'type': 'level_advance', 
                    'spin': self.fs + 1, 
                    'new_level': self.current_level,
                    'extra_spins_granted': spins_granted
                })
                #print(f"DEBUG: Level advanced to {self.current_level} with {spins_granted} extra spins at segment boundary")
            # Lock the new segment's level
            self.segment_level = self.current_level
            # After first segment, all subsequent segments are 10 spins
            self.current_segment_length = 10
            #print(f"DEBUG: New segment started at level {self.segment_level}")
        
        # Emit spinWinTotal event after all collections are processed
        spin_win_total_event(self, self.spin_line_wins, self.spin_collections)
        
        # Now emit standard win events - win_manager.spin_win already contains total amount
        from src.events.events import set_win_event, set_total_event
        if self.win_manager.spin_win > 0:
            set_win_event(self)
        set_total_event(self)


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