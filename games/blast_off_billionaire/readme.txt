Blast Off Billionaire - Stake Engine Math SDK Game

OVERVIEW:
A multiplier-based slot game with no reels or symbols. Players have a 50/50 chance to win or lose on each spin. Winners receive a random multiplier between 0.1x and 5000x applied to their bet.

GAME MECHANICS:
- 55% chance to lose (win = 0)
- 45% chance to win with weighted multiplier selection
- Multiplier ranges: 0.1x to 5000x with configurable weights
- Target RTP: 95% (adjustable via optimization)
- Wincap: 5000x

TECHNICAL DETAILS:
- No reels or traditional symbols required
- Uses weighted distribution system for multiplier selection
- Compatible with Stake Engine's book generation and optimization systems
- Supports easy RTP tweaking via multiplier_optimization.py
- Simple optimization system that adjusts 0-1x multiplier weights to hit target RTP

FILES:
- game_config.py: Game configuration and multiplier ranges
- game_calculations.py: Multiplier selection logic
- game_executables.py: Spin execution
- game_events.py: Event generation for books
- game_override.py: Custom state overrides
- gamestate.py: Main simulation controller
- multiplier_optimization.py: Simplified multiplier-based RTP optimization
- run.py: Simulation entry point

USAGE:
Run simulation: python run.py
Or via make: make run GAME=blast_off_billionaire