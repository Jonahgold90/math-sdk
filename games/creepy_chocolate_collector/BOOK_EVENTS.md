# Creepy Chocolate Collector - Book Events Documentation

This document describes all events emitted by the Creepy Chocolate Collector game for frontend integration.

## Bet Modes

The game supports three bet modes:

### Base Mode
- **Cost**: 1.0x bet
- **Feature frequency**: 1 in 100 spins (average)
- **Description**: Standard gameplay with normal scatter hit rate

### Anti Bet Mode 
- **Cost**: 1.5x bet (50% increase)
- **Feature frequency**: 1 in 67 spins (average) - 50% more frequent
- **Description**: Higher cost mode with increased scatter hit rate for more bonus triggers
- **Use case**: Players who want more frequent bonuses at higher cost

### Bonus Buy Mode
- **Cost**: 100x bet
- **Feature frequency**: Guaranteed bonus
- **Description**: Direct purchase of bonus round

## Event Structure

All events are stored in the `events` array within each book. Each event has a `type` field and additional properties specific to that event type.

## Base Game Events (Base & Anti Bet Modes)

The following events are shared between Base Mode and Anti Bet Mode, as they use identical game mechanics - only the scatter frequency differs.

### `reveal`
Board reveal for each spin.
```json
{
  "type": "reveal",
  "board": [
    [
      {"name": "L2"},
      {"name": "H1"},
      {"name": "JAR", "scatter": true}
    ]
  ],
  "paddingPositions": [70, 162, 212],
  "gameType": "basegame",
  "anticipation": [0, 0, 1, 2]
}
```

### `setTotalWin`
Sets the total win amount for the spin.
```json
{
  "type": "setTotalWin",
  "amount": 500
}
```

### `spinWinTotal` ⭐ **NEW COMPLETE WIN EVENT**
Provides complete spin total breakdown for win animations.
```json
{
  "type": "spinWinTotal",
  "amount": 227,
  "lineWins": 200,
  "collections": 27
}
```

**Fields:**
- `amount`: Total win for the spin (line wins + collections)
- `lineWins`: Win amount from line wins only
- `collections`: Win amount from collection events only

**Usage:**
- Emitted after all collections are processed for the spin
- Frontend can use `amount` directly for win animations
- Eliminates need for complex calculations and timing issues
- Always provides accurate, complete spin totals

### `winInfo`
Details about line wins on the current spin.
```json
{
  "type": "winInfo",
  "totalWin": 500,
  "wins": [
    {
      "symbol": "H2",
      "kind": 4,
      "win": 500,
      "positions": [
        {"reel": 0, "row": 3},
        {"reel": 1, "row": 2}
      ],
      "meta": {
        "lineIndex": 13,
        "multiplier": 1,
        "winWithoutMult": 500,
        "globalMult": 1,
        "lineMultiplier": 1
      }
    }
  ]
}
```

### `freeSpinTrigger`
Triggered when 3+ scatter symbols appear in base game.
```json
{
  "type": "freeSpinTrigger",
  "totalFs": 10,
  "positions": [
    {"reel": 0, "row": 3},
    {"reel": 2, "row": 3},
    {"reel": 4, "row": 3}
  ]
}
```

## Bonus Game Events

### `updateFreeSpin`
Updates free spin count during bonus.
```json
{
  "type": "updateFreeSpin",
  "amount": 0,
  "total": 10
}
```

### `collection` ⭐ **NEW BIG-BASS EVENT**
Emitted when Collector Wilds (CW) collect Chocolate Cash (CC) symbols.
```json
{
  "type": "collection",
  "spin": 11,
  "level": 2,
  "cw_count": 2,
  "cc_count": 1,
  "cc_values": [5],
  "cc_sum": 5,
  "collected_amount": 10,
  "payout_per_cw_raw": 5,
  "subcollections": [
    {"cw_index": 0, "amount": 5},
    {"cw_index": 1, "amount": 5}
  ]
}
```

**Collection Event Fields:**
- `spin`: Current spin number when collection occurred
- `level`: Segment-locked multiplier level (1-4)
- `cw_count`: Number of Collector Wild symbols on board
- `cc_count`: Number of Chocolate Cash symbols on board
- `cc_values`: Array of individual CC cash values
- `cc_sum`: Total sum of all CC values
- `collected_amount`: Final amount credited (may be capped)
- `payout_per_cw_raw`: Raw payout per CW before capping (cc_sum × level_multiplier)
- `subcollections`: Array showing payout distribution per CW (handles remainder)

### `level_advance` ⭐ **NEW BIG-BASS EVENT**
Emitted when the multiplier level advances at segment boundaries. Also grants retrigger spins.
```json
{
  "type": "level_advance",
  "spin": 11,
  "new_level": 2,
  "extra_spins_granted": 10
}
```

**Level Advance Fields:**
- `spin`: Spin number when level advance occurred
- `new_level`: New multiplier level (2, 3, or 4)
- `extra_spins_granted`: Number of extra spins granted with this level-up (10 per retrig)

### `setWin`
Sets win amount and win level for current spin.
```json
{
  "type": "setWin",
  "amount": 500,
  "winLevel": 5
}
```

### `freeSpinEnd`
Marks the end of the bonus round.
```json
{
  "type": "freeSpinEnd",
  "amount": 500,
  "winLevel": 3
}
```

### `finalWin`
Final win amount for the entire game round.
```json
{
  "type": "finalWin",
  "amount": 500
}
```

## Big-Bass Mechanics Overview

### Level System
- **4 Levels**: Level 1 (x1), Level 2 (x2), Level 3 (x3), Level 4 (x10)
- **Segment-based**: Levels are locked for variable-length segments
- **First Segment**: Length matches initial bonus (10/15/20 spins based on scatter count)
- **Subsequent Segments**: Always 10 spins each
- **Progression**: Every 4 Collector Wilds queue a level-up and retrigger
- **Advancement**: Level-ups and retriggers occur at segment boundaries
- **Maximum Retrigs**: 3 total (one each for levels 2, 3, and 4)

### Collection Formula
```
collected_amount = cc_sum × cw_count × level_multiplier
```

### Event Flow Example (15-spin initial bonus)
1. Player gets 4 scatters → 15 initial spins
2. Player hits 4 CWs on spin 2 → Level-up and retrigger queued
3. Spins 3-15 continue at Level 1 (segment-locked)
4. Spin 16 → `level_advance` event with `extra_spins_granted: 10` → Level 2 begins with 10 extra spins
5. CW+CC combination on spin 16 → `collection` event at Level 2 (x2 multiplier)

## Frontend Integration Notes

### For Collection Animation
- Use `cw_count` and `cc_count` to display and animate collecting symbols
- Use `subcollections` array to show individual CW payouts
- Display `level` to show current multiplier
- Use `collected_amount` for final payout display

### For Level Progression UI
- Track `level_advance` events to trigger level-up animations
- Use `extra_spins_granted` field to display retrigger notifications
- Show progression toward next level based on CW accumulation  
- Display current segment's locked multiplier
- Show remaining spins counter (including retriggered spins)

### For Statistics/RTP
- Sum all `collected_amount` values for total collection contribution
- Track level distribution from `level_advance` events
- Monitor collection frequency and values by level

## Symbol Definitions

- **CW (Collector Wild)**: Special wild symbol that collects chocolate cash (freegame mode only)
- **CC (Chocolate Cash)**: Cash symbols with `cash_value` attribute (2-2000x bet)
- **JAR**: Scatter symbol that triggers free spins (3+ required)
- **H1-H4**: High-value regular symbols
- **L1-L5**: Low-value regular symbols