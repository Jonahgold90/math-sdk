# Brainrot Bonanza - Book Events Documentation

This document describes all events emitted by the Brainrot Bonanza game for frontend integration.

## Game Overview

**Brainrot Bonanza** is a 6×5 pay-anywhere tumbling slot with:
- **Win Type**: True pay-anywhere (8+ symbols of same type anywhere on board)
- **Tumbling**: Winning symbols removed, new ones fall down until no more wins
- **Free Spins**: 4+ scatters → 10 free spins
- **Multipliers**: Only in free spins, sum all M symbols and multiply tumble chain total
- **Win Cap**: 25,000× bet maximum

## Bet Modes

### Base Mode
- **Cost**: 1.0× bet
- **Feature frequency**: ~1 in 200 spins (natural scatter triggers)
- **Description**: Standard gameplay with regular scatter hit rate

### Bonus Buy Mode
- **Cost**: 100× bet
- **Feature frequency**: Guaranteed 4+ scatters on entry spin
- **Description**: Direct purchase of bonus round with guaranteed free spin trigger

## Event Structure

All events are stored in the `events` array within each book. Each event has a `type` field and additional properties specific to that event type.

## Base Game Events

### `reveal`
Board reveal for each spin with 6×5 grid.
```json
{
  "type": "reveal",
  "board": [
    [
      {"name": "L4"},
      {"name": "H2"},
      {"name": "L4"},
      {"name": "H3"},
      {"name": "H3"},
      {"name": "L2"}
    ],
    [
      {"name": "L4"},
      {"name": "H4"},
      {"name": "H3"},
      {"name": "L1"},
      {"name": "L2"},
      {"name": "L1"}
    ],
    [
      {"name": "L1"},
      {"name": "H4"},
      {"name": "H2"},
      {"name": "L4"},
      {"name": "H4"},
      {"name": "L2"}
    ],
    [
      {"name": "H3"},
      {"name": "L3"},
      {"name": "L4"},
      {"name": "H3"},
      {"name": "L4"},
      {"name": "L4"}
    ],
    [
      {"name": "L3"},
      {"name": "L1"},
      {"name": "L3"},
      {"name": "L3"},
      {"name": "H2"},
      {"name": "L2"}
    ],
    [
      {"name": "L2"},
      {"name": "H1"},
      {"name": "H2"},
      {"name": "L2"},
      {"name": "L2"},
      {"name": "L2"}
    ]
  ],
  "paddingPositions": [216, 205, 195, 16, 65, 30],
  "gameType": "basegame",
  "anticipation": [0, 0, 0, 0, 0, 1]
}
```

**Fields:**
- `board`: 6×5 array of symbols (reel × row format)
- `paddingPositions`: Reel strip positions for each reel
- `gameType`: Either "basegame" or "freegame"
- `anticipation`: Array showing scatter anticipation values per reel

### `winInfo`
Details about scatter wins on the current tumble.
```json
{
  "type": "winInfo",
  "totalWin": 80,
  "wins": [
    {
      "symbol": "L2",
      "win": 80,
      "positions": [
        {"reel": 0, "row": 5},
        {"reel": 3, "row": 1},
        {"reel": 3, "row": 2},
        {"reel": 4, "row": 1},
        {"reel": 4, "row": 2},
        {"reel": 4, "row": 3},
        {"reel": 5, "row": 2},
        {"reel": 5, "row": 3}
      ],
      "meta": {
        "globalMult": 1,
        "clusterMult": 1,
        "winWithoutMult": 80,
        "overlay": {
          "reel": 4,
          "row": 3
        }
      }
    }
  ]
}
```

**Fields:**
- `totalWin`: Total win amount for this tumble
- `wins`: Array of winning symbol combinations
- `symbol`: Symbol name that won (H1-H4, L1-L4, S)
- `win`: Win amount for this symbol combination
- `positions`: Array of all positions where this symbol appeared
- `meta.globalMult`: Global multiplier (always 1 in base game)
- `meta.clusterMult`: Symbol-specific multiplier (usually 1)
- `meta.winWithoutMult`: Base win before multipliers
- `meta.overlay`: Suggested position for win display overlay

### `updateTumbleWin`
Updates the cumulative tumble win amount.
```json
{
  "type": "updateTumbleWin",
  "amount": 80
}
```

### `tumbleBoard`
Describes symbol removal and replacement during tumbling.
```json
{
  "type": "tumbleBoard",
  "newSymbols": [
    [{"name": "H2"}],
    [],
    [],
    [{"name": "H1"}, {"name": "L2"}],
    [{"name": "L3"}, {"name": "L1"}, {"name": "L3"}],
    [{"name": "H4"}, {"name": "H3"}]
  ],
  "explodingSymbols": [
    {"reel": 0, "row": 5},
    {"reel": 3, "row": 1},
    {"reel": 3, "row": 2},
    {"reel": 4, "row": 1},
    {"reel": 4, "row": 2},
    {"reel": 4, "row": 3},
    {"reel": 5, "row": 2},
    {"reel": 5, "row": 3}
  ]
}
```

**Fields:**
- `newSymbols`: Array of new symbols falling into each reel (top to bottom order)
- `explodingSymbols`: Array of positions that were removed from the board

### `setWin`
Sets win amount and win level for current tumble.
```json
{
  "type": "setWin",
  "amount": 80,
  "winLevel": 2
}
```

### `setTotalWin`
Sets the total win amount for the entire spin.
```json
{
  "type": "setTotalWin",
  "amount": 80
}
```

### `freeSpinTrigger`
Triggered when 4+ scatter symbols appear.
```json
{
  "type": "freeSpinTrigger",
  "totalFs": 10,
  "positions": [
    {"reel": 1, "row": 5},
    {"reel": 2, "row": 2},
    {"reel": 3, "row": 3},
    {"reel": 4, "row": 1}
  ]
}
```

**Fields:**
- `totalFs`: Number of free spins granted (always 10 for 4+ scatters)
- `positions`: Positions of scatter symbols that triggered the bonus

### `finalWin`
Final win amount for the entire game round.
```json
{
  "type": "finalWin",
  "amount": 80
}
```

## Free Game Events

### `updateFreeSpin`
Updates free spin counter during bonus.
```json
{
  "type": "updateFreeSpin",
  "amount": 1,
  "total": 10
}
```

**Fields:**
- `amount`: Current free spin number (1-based)
- `total`: Total free spins for this bonus

### `updateGlobalMult`
Updates the global multiplier (always 1 at the start of each freespin in this game).
```json
{
  "type": "updateGlobalMult",
  "globalMult": 1
}
```

### `multiplierLanded` ⭐ **NEW MULTIPLIER LANDING EVENT**
Emitted when multiplier (M) symbols land on the board during free spins.
```json
{
  "type": "multiplierLanded",
  "multipliers": [
    {"reel": 1, "row": 6, "value": 4.0},
    {"reel": 2, "row": 4, "value": 2.0}
  ],
  "totalMultipliers": 3,
  "boardMultiplierSum": 9.0
}
```

**Fields:**
- `multipliers`: Array of multiplier symbols that just landed
- `reel`: Reel position (0-5)
- `row`: Row position (0-6, includes padding)
- `value`: Multiplier value (2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 50, 100, 1000)
- `totalMultipliers`: Total count of M symbols currently on board
- `boardMultiplierSum`: Sum of all M symbol values on board

**Timing:**
- Emitted after `reveal` event if M symbols present on initial spin
- Emitted after `tumbleBoard` event if new M symbols fall down during tumbles
- **NOT emitted** if no new M symbols land (even if existing ones persist)

**Usage:**
- Frontend can animate M symbols landing with visual effects
- Update multiplier counter UI in real-time
- Show individual multiplier values as they land
- Build anticipation for final collection moment

### `boardMultiplierInfo` ⭐ **KEY MULTIPLIER COLLECTION EVENT**
Provides multiplier information when M symbols are present and wins occur.
```json
{
  "type": "boardMultiplierInfo",
  "multInfo": {
    "positions": [
      {"reel": 2, "row": 5, "multiplier": 5.0}
    ]
  },
  "winInfo": {
    "tumbleWin": 840,
    "boardMult": 5.0,
    "totalWin": 4200
  }
}
```

**Fields:**
- `multInfo.positions`: Array of multiplier symbol positions and values
- `winInfo.tumbleWin`: Win amount before multiplier applied
- `winInfo.boardMult`: Sum of all multipliers on board
- `winInfo.totalWin`: Final win after multiplier (tumbleWin × boardMult)

**Usage:**
- **Animation**: Use `positions` to highlight multiplier symbols during collection
- **Math**: Shows the exact calculation of multiplier application
- **Display**: Use `boardMult` to show total multiplier, `totalWin` for final amount

### `freeSpinEnd`
Marks the end of the bonus round.
```json
{
  "type": "freeSpinEnd",
  "amount": 8490,
  "winLevel": 6
}
```

## Special Symbol Events

### Multiplier Symbol (M) - Free Spins Only
Multiplier symbols appear only during free spins with the following properties:
```json
{"name": "M", "multiplier": 4}
```

**Multiplier Values**: {2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 50, 100, 1000}×
**Frequency**: ~1.5 multipliers per free spin on average
**Mechanics**:
- Sum all multipliers on board at end of tumble chain
- Multiply the entire tumble chain total win
- Clear before next free spin (not sticky)

### Scatter Symbol (S)
Scatter symbols trigger free spins and appear in both base and free games:
```json
{"name": "S", "scatter": true}
```

**Trigger Requirements**:
- **Base Game**: 4+ scatters → 10 free spins
- **Free Spins**: 3+ scatters → +5 free spins (retrigger)

## Pay Anywhere Mechanics

### Symbol Requirements
All regular symbols (H1-H4, L1-L4) require **8+ instances** anywhere on the 6×5 board to win.

### Paytable (8+/10-11/12+ symbol counts)
```
H1: 10.00 / 25.00 / 50.00
H2:  2.50 / 10.00 / 25.00
H3:  2.00 /  5.00 / 15.00
H4:  1.50 /  2.00 / 12.00
L1:  1.00 /  1.50 / 10.00
L2:  0.80 /  1.00 /  8.00
L3:  0.50 /  1.00 /  5.00
L4:  0.40 /  0.90 /  4.00
```

### Scatter Pays (4/5/6+ symbols)
```
S: 3.00 / 5.00 / 100.00
```

## Tumbling Sequence

The tumbling sequence follows this pattern:

1. **Initial Reveal**: `reveal` event with full board
2. **Win Detection**: `winInfo` event if 8+ symbols found
3. **Win Update**: `updateTumbleWin` event with cumulative amount
4. **Symbol Removal**: `tumbleBoard` event removing winning symbols
5. **Repeat**: Steps 2-4 until no more wins
6. **Multiplier Application**: `boardMultiplierInfo` (free spins only)
7. **Final Amounts**: `setWin` and `setTotalWin` events

## Frontend Integration Notes

### For Tumbling Animation
- **Use `tumbleBoard`**: Shows exactly which symbols to remove and what falls down
- **Sequential Processing**: Process tumbles one at a time in event order
- **Position Mapping**: Use `explodingSymbols` for removal animations
- **New Symbols**: Use `newSymbols` for falling animations (top-to-bottom order)

### For Win Display
- **Use `winInfo`**: Shows winning symbol combinations and positions
- **Overlay Position**: Use `meta.overlay` for win amount display positioning
- **Running Total**: Track `updateTumbleWin` for cumulative tumble total

### For Multiplier Animation (Free Spins)
- **Landing Animation**: Use `multiplierLanded` for M symbols appearing on board
  - Animate individual M symbols as they land with their values
  - Update running multiplier counter UI
  - Build anticipation throughout the tumble chain
- **Collection Animation**: Use `boardMultiplierInfo` for final multiplier application
  - Highlight all M symbols during collection moment
  - Show calculation: `tumbleWin × boardMult = totalWin`
  - Display final multiplied win amount
- **Timing**: `multiplierLanded` fires during spins, `boardMultiplierInfo` fires at end

### For Scatter Triggers
- **Use `freeSpinTrigger`**: Shows scatter positions and free spin count
- **Animation**: Highlight `positions` array for scatter celebration
- **Retriggers**: Track during free spins for additional free spins

### For Statistics/Analysis
- **Tumble Chains**: Count `tumbleBoard` events per spin for cascade length
- **Hit Frequency**: Track `winInfo` events for win rate analysis
- **Multiplier Impact**: Use `boardMultiplierInfo` to measure multiplier contribution
- **Bonus Frequency**: Track `freeSpinTrigger` events for trigger rate

## Symbol Definitions

- **H1-H4**: High-value regular symbols (premium pays)
- **L1-L4**: Low-value regular symbols (reduced from L1-L5 to increase hit frequency)
- **S (Scatter)**: Triggers free spins (4+ in base, 3+ in free for retrigger)
- **M (Multiplier)**: Free spins only, multiplies tumble chain total (2x-1000x values)

## Key Differences from Other Games

1. **Pay-Anywhere**: No paylines or adjacency required, just symbol count
2. **Tumbling**: Cascading wins with symbol removal and replacement
3. **Multiplier Timing**: Applied to entire tumble chain total, not individual tumbles
4. **Grid Size**: 6×5 instead of typical 5×3
5. **8+ Symbol Requirement**: Higher threshold than typical 3-5 symbol games