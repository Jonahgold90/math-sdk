# Gates of Olympus - Technical Specification

## Game Overview
**Game Name:** Gates of Olympus  
**Game Type:** Scatter Pay (8+ symbols anywhere)  
**Grid:** 6×5  
**Volatility:** High  
**Max Win:** 5,000× total bet  
**RTP Target:** 96.00%  

## Core Mechanics

### 1. Win Calculation System
- **Win Type:** Scatter pay system
- **Minimum Win:** 8 matching symbols anywhere on grid
- **Symbol Evaluation:** Position-independent (scatter pays)
- **Win Tiers:** 8, 9, 10-11, 12-13, 14+ symbols (adjust ranges as needed)

### 2. Tumble Feature
- **Trigger:** After every spin (base game and free spins)
- **Behavior:** 
  - Remove all winning symbols from grid
  - Remaining symbols fall down to fill gaps
  - New symbols drop from top to fill empty positions
  - Process continues until no new wins form
- **Win Accumulation:** All tumble wins are summed and paid together

### 3. Multiplier System

#### Base Game Multipliers
- **Appearance:** Random on any position during any spin
- **Values:** ×2, ×3, ×4, ×5, ×6, ×8, ×10, ×12, ×15, ×20, ×25, ×50, ×100, ×250, ×500
- **Application:** Applied at end of tumble sequence to total wins
- **Behavior:** All multiplier values on screen are additive

#### Free Spins Multipliers
- **Global Multiplier:** Persistent accumulating multiplier (starts at 0×)
- **Trigger:** When multiplier symbol appears AND a win occurs in same tumble sequence
- **Accumulation:** Multiplier values added to global multiplier during the sequence
- **Application:** New global multiplier total applies to that same tumble sequence's wins
- **Example:** Global at 5×, tumble has ×10 multiplier + wins → Global becomes 15×, wins get multiplied by 15×

### 4. Free Spins Feature

#### Trigger Conditions
- **Base Game:** 4+ scatter symbols in single spin
- **Free Spins:** 3+ scatter symbols retrigger (+5 spins)
- **Award:** 15 free spins initially

#### Free Spins Mechanics
- Uses special reel sets (higher volatility)
- Global multiplier system active
- Multipliers accumulate when wins occur
- Additional spins possible via retrigger

### 5. Ante Bet System

#### Standard Bet (1×)
- **Features:** Enables Buy Free Spins option
- **Buy Cost:** 100× total bet
- **Scatter Frequency:** Standard reel configuration

#### Ante Bet (1.25×)
- **Cost:** 1.25× base bet (25% more)
- **Features:** 
  - Doubled free spin trigger chance
  - Higher scatter symbol frequency on reels
  - Disables Buy Free Spins option

## Symbol Configuration

### Regular Pay Symbols
Based on Gates of Olympus theme:
- **High Symbols:** H1 (Crown), H2 (Chalice), H3 (Horn), H4 (Ring)
- **Low Symbols:** L1 (Red Gem), L2 (Purple), L3 (Yellow), L4 (Green), L5 (Blue)

### Special Symbols
- **Scatter:** Zeus (triggers free spins)
- **Multiplier:** Orb/Lightning (carries multiplier values)
- **Wild:** Not present in original game

### Paytable Structure
```
Symbol | 8-9 pays | 10-11 pays | 12-30 pays
-------|----------|------------|------------
H1     | 10.00×   | 25.00×     | 50.00×
H2     | 2.50×    | 10.00×     | 25.00×
H3     | 2.00×    | 5.00×      | 15.00×
H4     | 1.50×    | 2.00×      | 12.00×
L1     | 1.00×    | 1.50×      | 10.00×
L2     | 0.80×    | 1.20×      | 8.00×
L3     | 0.50×    | 1.00×      | 5.00×
L4     | 0.40×    | 0.90×      | 4.00×
L5     | 0.25×    | 0.75×      | 2.00×
```

**Scatter Symbol (Zeus):**
- 4 Scatters: 3.00×
- 5 Scatters: 5.00×  
- 6 Scatters: 100.00×

## Reel Configuration

### Base Game Reels (BR0)
- Standard symbol distribution
- Moderate scatter frequency
- Balanced multiplier appearance

### Ante Bet Reels
- Increased scatter symbol frequency (2× trigger chance)
- Maintained symbol balance for RTP

### Free Spins Reels (FR0)
- Higher volatility distribution
- Increased multiplier symbol frequency
- Different symbol ratios for bonus gameplay

## Technical Implementation Requirements

### Game State Changes from Template
1. **Symbol Set:** Update to 9 regular symbols (4 high H1-H4, 5 low L1-L5)
2. **Multiplier Values:** Implement 15 different multiplier values
3. **Global Multiplier:** Add persistent multiplier for free spins
4. **Ante Bet:** Implement 1.25x ante bet mode with different reels
5. **Buy Feature:** 100× buy option (disabled in ante mode)

### Key Modifications Needed

#### Game Config Changes
- Update `game_id` and `game_name` to "gates"
- Modify `wincap` to 5000.0
- Update paytable with 9 symbol configuration (H1-H4, L1-L5)
- Add ante bet mode configuration
- Configure multiplier value ranges

#### Reel Updates
- Create ante bet reel sets with increased scatters
- Adjust free spin reels for higher volatility
- Balance multiplier symbol frequency

#### Game Logic Updates
- Implement global multiplier accumulation in free spins
- Add ante bet mode switching logic
- Update buy feature availability based on bet mode
- Modify multiplier application timing

#### Event System
- Global multiplier accumulation events
- Ante bet mode selection events
- Enhanced multiplier value assignment

## Mathematical Targets

###96% RTP

### Volatility Targets
- **Hit Frequency:** ~25-30% (base game)
- **Free Spin Frequency:** ~1 in 100-150 spins (standard bet)
- **Free Spin Frequency:** ~1 in 50-75 spins (ante bet)
- **Max Win Probability:** ~1 in 50,000-100,000

### Key Performance Indicators
- Average free spin win: 50-100× bet
- Multiplier contribution: 20-30% of total RTP
- Tumble feature contribution: 40-50% of total RTP
- Maximum tumble sequence: 10+ cascades possible

## Implementation Priority
1. Core scatter pay system (already functional)
2. Enhanced multiplier system with 15 values
3. Global multiplier for free spins
4. Ante bet mode implementation
5. Buy feature integration
6. Reel optimization and balancing