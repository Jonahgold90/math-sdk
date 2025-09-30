# Brainrot Bonanza — Math Spec (SB1000 Clone, No Super Buy)

## Core
- **Grid:** 6×5 (30 symbols visible each spin)
- **Pays:** True Pay-Anywhere (wins by total symbol count on board, symbols don't need to be connected)
- **Tumble:** Winning symbols are removed, new ones fall until no wins remain
- **Symbol Generation:** Independent weighted selection per cell position (no fixed reel strips)
- **Free Spins:** 4+ `scatter` → 10 free spins, retrigger 3+ → +5 spins
- **Multiplier symbols:**
  - Appear only in FS (weight = 0 in base game)
  - Don't need to be connected to wins
  - Persist for current tumble chain only
  - Sum all visible multipliers and apply to tumble chain's subtotal
  - Clear before next FS spin (not sticky across spins)
- **Max Win:** 25,000× bet (hard cap)
- **Ante Bet:**
  - Off (1x base bet): Normal play, Bonus Buy enabled
  - On (1.25× base bet): Increases FS hit rate (e.g., 1/100 vs 1/200), Bonus Buy disabled
- **Bonus Buy:** 100× bet → guarantees 4+ `scatter` on the entry spin
- **RTP targets:**
  - 96% for all modes

---

## Symbols
- **Regular symbols:** 8 total (h1–h4 high pays, l1–l4 low pays)
- **Special symbols:** scatter, multiplier (FS only)
- **Total unique symbols:** 10

## Paytable (multipliers of base bet)

### Premiums
| Symbol | 12+ | 10–11 | 8–9 |
|--------|-----|-------|-----|
| **h1** | 50.00 | 25.00 | 10.00 |
| **h2** | 25.00 | 10.00 | 2.50 |
| **h3** | 15.00 | 5.00  | 2.00 |
| **h4** | 12.00 | 2.00  | 1.50 |

### Lows
| Symbol | 12+ | 10–11 | 8–9 |
|--------|-----|-------|-----|
| **l1** | 10.00 | 1.50 | 1.00 |
| **l2** | 8.00  | 1.00 | 0.80 |
| **l3** | 5.00  | 1.00 | 0.50 |
| **l4** | 4.00  | 0.90 | 0.40 |

### Scatter
- **Label:** `scatter`  
- Pays anywhere:  
  - 4 = 3.00×  
  - 5 = 5.00×  
  - 6 = 100.00×  
- Triggers FS with 4+ scatters  

### Multiplier (FS-only)
- **Label:** `multiplier`
- Values (weighted in rarity so 1000x extremely rare 2x common): {2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 50, 100, 1000}×
- At end of each tumble chain, sum all multipliers on screen and apply to that tumble chain's total win
- Clears before next FS spin (not sticky)

---

## Symbol Weight Sets

### Base Game Weights
- Regular symbols (h1-h4, l1-l4): Weighted for target hit rate
- scatter: Low weight for ~1/200 FS trigger rate (ante off)
- multiplier: Weight = 0 (never appears)

### Free Spins Weights
- Regular symbols (h1-h4, l1-l4): Similar to base
- scatter: Weight for retrigger potential
- multiplier: Active weight for multiplier symbols

### Ante Bet Adjustment
- When ante bet is ON (1.25x cost):
  - Adjusts FS hit rate to ~1/100 (optimization parameter)
  - Same symbol weights, different distribution quotas

---

