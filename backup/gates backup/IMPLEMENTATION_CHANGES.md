# Gates of Olympus - Required Changes from Scatter Template

## Key Differences Summary

### 1. Multiplier System Changes
**Current Template:**
- 5 multiplier values: ×2, ×4, ×5, ×7, ×10
- Simple additive multipliers per tumble sequence

**Gates of Olympus Required:**
- 15 multiplier values: ×2, ×3, ×4, ×5, ×6, ×8, ×10, ×12, ×15, ×20, ×25, ×50, ×100, ×250, ×500
- Global accumulating multiplier system in free spins
- Multipliers only accumulate when wins occur

### 2. Symbol Configuration
**Current Template:**
- 8 regular symbols (H1-H4, L1-L4)
- Generic scatter template symbols

**Gates of Olympus Required:**
- 8 themed symbols (Crown, Ring, Hourglass, Chalice, Red Gem, Blue Gem, Green Gem, Purple Gem)
- Zeus scatter symbol
- Lightning/Orb multiplier symbols

### 3. Free Spins Mechanics
**Current Template:**
- Standard free spins with retrigger
- Various scatter trigger amounts (3-10 scatters)
- No global multiplier system

**Gates of Olympus Required:**
- 15 free spins from 4+ scatters
- +5 spins from 3+ scatters during bonus
- Global multiplier accumulation system
- Multipliers only add to global when wins occur

### 4. Bet Mode System
**Current Template:**
- Base bet mode (1×)
- Buy bonus mode (200×)

**Gates of Olympus Required:**
- Standard bet mode (20×) - enables buy feature
- Ante bet mode (1.25×) - doubles scatter chance, disables buy
- Buy feature cost: 100× (not 200×)

### 5. Game Identity
**Current Template:**
- game_id: "0_0_scatter"
- game_name: "sample_scatter"

**Gates of Olympus Required:**
- game_id: "gates"
- game_name: "Gates of Olympus"

## Specific Files Requiring Changes

### 1. game_config.py
- [ ] Update game identity (lines 19-22)
- [ ] Modify paytable for 8 symbols with proper payouts
- [ ] Expand multiplier values to 15 options (lines 130-132, 147-149, etc.)
- [ ] Update freespin triggers to 4+ scatters = 15 spins, 3+ = +5 retrigger
- [✅] Add ante bet mode with 1.25× cost and modified reel weights
- [ ] Update buy bonus cost to 100×

### 2. gamestate.py
- [ ] Implement global multiplier system for free spins
- [ ] Modify multiplier accumulation logic (only when wins occur)
- [ ] Update free spin initialization to reset global multiplier

### 3. game_override.py
- [ ] Add global multiplier management methods
- [ ] Implement ante bet mode logic
- [ ] Override multiplier application for free spins

### 4. Reel Files
- [ ] Create ante bet reel variants (increased scatter frequency)
- [ ] Update symbol distributions for themed symbols
- [ ] Balance multiplier symbol frequency

### 5. game_events.py
- [ ] Add global multiplier accumulation events
- [ ] Update multiplier value assignment events

## Critical Implementation Points

### Global Multiplier Logic
```python
# Free spins only - accumulate when win occurs
if self.gametype == self.freegame_type and self.win_data["totalWin"] > 0:
    for mult_symbol in multiplier_symbols_on_board:
        self.global_multiplier += mult_symbol.value
```

### Ante Bet Mode Selection
- Mutually exclusive with buy feature
- Changes reel sets used
- Affects scatter frequency

### Enhanced Multiplier Values
- Need weighted distribution for 15 different values
- Higher values should be rarer
- Maintain mathematical balance

## Next Steps Priority
1. Update game identity in config
2. Implement 15-value multiplier system
3. Add global multiplier logic
4. Create ante bet mode
5. Update reel configurations
6. Balance mathematical model