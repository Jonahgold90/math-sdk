# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup and Installation
```bash
# Initial setup (creates virtual environment and installs dependencies)
make setup

# Alternative manual setup
python3 -m venv env
# Windows: env\Scripts\activate.bat
# Unix/macOS: source env/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Running Games
```bash
# Run a specific game simulation
make run GAME=<game_name>
# Example: make run GAME=0_0_lines
# Example: make run GAME=template

# Direct game execution
python games/<game_name>/run.py
```

### Testing
```bash
# Run test suite
make test
# or
pytest tests/
```

### Utilities
```bash
# Clean build artifacts
make clean

# Format books JSON files (when compression is disabled)
python utils/format_books_json.py games/<game_name>

# Verify RGS data
python utils/rgs_verification.py

# Run game analytics
python utils/game_analytics/run_analysis.py
```

## Architecture Overview

### Core Components

**Game State Machine**: The engine follows a state-based simulation model where each game inherits from `GeneralGameState` (src/state/state.py). Games define their logic through:
- `GameState`: Main simulation controller (games/*/gamestate.py)
- `GameConfig`: Game-specific configuration (games/*/game_config.py)  
- `GameOverride`: Custom game logic overrides (games/*/game_override.py)

**Module Structure**:
- `src/state/`: Core state management and simulation engine
- `src/config/`: Configuration system, bet modes, and game parameters
- `src/calculations/`: Win calculation engines (lines, ways, scatter, cluster, etc.)
- `src/events/`: Event system for game features and triggers
- `src/executables/`: Game execution logic and workflow management
- `src/wins/`: Win management and multiplier strategies
- `src/write_data/`: Output generation and data serialization

**Game Types**: The engine supports multiple calculation types:
- Lines pay (traditional paylines)
- Ways pay (adjacent symbol matching)
- Scatter pay (position-independent symbols)
- Cluster pay (connected symbol groups)
- Tumble mechanics

### Game Development Pattern

Each game follows a standardized structure in `games/<game_name>/`:
- `gamestate.py`: Inherits from template, defines spin logic
- `game_config.py`: Game-specific settings, paytables, and RTP
- `game_calculations.py`: Custom calculation overrides
- `game_events.py`: Game feature events and triggers
- `game_executables.py`: Execution flow customization
- `game_optimization.py`: RTP optimization parameters
- `run.py`: Entry point for simulation execution
- `reels/`: CSV files containing reel strip definitions

### Optimization System

The engine includes a Rust-based optimization program (`optimization_program/`) for RTP distribution optimization. The Rust component provides high-performance number crunching for complex mathematical calculations.

### Output and Data Flow

Games generate multiple outputs:
- Lookup tables for game logic
- Simulation results and statistics
- RGS (Remote Game Server) compatible data formats
- Books files for detailed game analysis
- AWS upload functionality for deployment

### Key Dependencies

- **Python 3.12+** required
- **Rust/Cargo** for optimization algorithms
- **pytest** for testing
- **boto3** for AWS integration
- **numpy** for numerical calculations
- **zstandard** for compression
- **mkdocs** for documentation generation

The engine emphasizes reproducible simulations, comprehensive testing, and scalable game development through its modular architecture.