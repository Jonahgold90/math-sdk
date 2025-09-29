#!/usr/bin/env python3
"""Run script for Blast Off Billionaire simulation."""

from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests


if __name__ == "__main__":
    # Simulation parameters
    num_threads = 3
    rust_threads = 4  # Threads for optimization
    sim_num = 230000
    batching_size = sim_num
    compression = True  # Set to True for production, False for debugging
    profiling = False
    
    # Number of simulations for base mode
    num_sim_args = {
        "base": sim_num,  
    }

    run_conditions = {
        "run_sims": True,
        "run_optimization": False,  # Disable Rust optimization temporarily
        "run_analysis": True,
        "run_format_checks": True,
    }
    target_modes = ["base"]
    # Initialize game
    config = GameConfig()
    gamestate = GameState(config)
    if run_conditions["run_optimization"] or run_conditions["run_analysis"]:
        optimization_setup_class = OptimizationSetup(config)

    # Display game information
    print(f"Starting {config.working_name} simulation...")
    print(f"Game ID: {config.game_id}")
    print(f"Target RTP: {config.rtp}")
    print(f"Wincap: {config.wincap}")
    total_sims = sum(num_sim_args.values())
    print(f"Simulations: {total_sims:,}")
    print("-" * 50)

    # Run the simulation
    if run_conditions["run_sims"]:
        create_books(
            gamestate,
            config,
            num_sim_args,
            batching_size,
            num_threads,
            compression,
            profiling,
        )

    # Generate configuration files
    generate_configs(gamestate)
    
    if run_conditions["run_optimization"]:
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        generate_configs(gamestate)

    if run_conditions["run_analysis"]:
        custom_keys = [
            {"symbol": "multiplier"},  # All multiplier wins
            {"symbol": "loss"},  # All losses
            {"symbol": "multiplier", "kind": "0-1"},  # 0-1x multipliers
            {"symbol": "multiplier", "kind": "1-2"},  # 1-2x multipliers
            {"symbol": "multiplier", "kind": "2-5"},  # 2-5x multipliers
            {"symbol": "multiplier", "kind": "5-10"},  # 5-10x multipliers
            {"symbol": "multiplier", "kind": "10-20"},  # 10-20x multipliers
            {"symbol": "multiplier", "kind": "20-50"},  # 20-50x multipliers
            {"symbol": "multiplier", "kind": "50-100"},  # 50-100x multipliers
            {"symbol": "multiplier", "kind": "100-200"},  # 100-200x multipliers
            {"symbol": "multiplier", "kind": "200-500"},  # 200-500x multipliers
            {"symbol": "multiplier", "kind": "500-1000"},  # 500-1000x multipliers
            {"symbol": "multiplier", "kind": "1000-2000"},  # 1000-2000x multipliers
            {"symbol": "multiplier", "kind": "2000-5000"},  # 2000-5000x multipliers
            {"symbol": "multiplier", "kind": "5000+"},  # 5000+ multipliers
        ]
        create_stat_sheet(gamestate, custom_keys=custom_keys)

    # Always generate stats_summary.json with multiplier-specific analysis
    from utils.multiplier_stats import create_multiplier_stats_summary
    create_multiplier_stats_summary(config, gamestate)
    
    if run_conditions["run_format_checks"]:
        execute_all_tests(config)
    
    print(f"\n{config.working_name} simulation completed successfully!")