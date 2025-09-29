"""Multiplier-aware statistics generation for crash-style games."""

import json
import os
from collections import defaultdict


def create_multiplier_stats_summary(config, gamestate=None):
    """
    Create stats_summary.json with multiplier-specific data for crash-style games.
    
    Args:
        config: Game configuration object
        gamestate: Optional gamestate for additional data
    """
    stats_path = os.path.join(config.library_path, "stats_summary.json")
    
    # Collect basic game information
    basic_stats = {
        "game_id": config.game_id,
        "target_rtp": config.rtp,
        "target_rtp_percentage": f"{config.rtp * 100:.1f}%",
        "wincap": config.wincap,
        "modes": []
    }
    
    # Analyze each bet mode
    for bet_mode in config.bet_modes:
        mode_name = bet_mode.get_name()
        mode_cost = bet_mode.get_cost()
        
        mode_stats = analyze_multiplier_mode(config, mode_name, mode_cost)
        mode_stats["name"] = mode_name
        mode_stats["cost"] = mode_cost
        
        # Ensure consistency by using force data as the primary source
        # If we have force data, recalculate RTP from it for accuracy
        if "total_events" in mode_stats and "multiplier_ranges" in mode_stats:
            # Recalculate RTP from force data to ensure consistency
            mode_stats = recalculate_rtp_from_force_data(mode_stats, config, mode_name, mode_cost)
        
        basic_stats["modes"].append(mode_stats)
    
    # Add meaningful multiplier range definitions that match our tracking system
    basic_stats["multiplier_ranges"] = {
        "0-1": {"min": 0.0, "max": 1.0, "description": "Sub-unit multipliers"},
        "1-2": {"min": 1.0, "max": 2.0, "description": "Low multipliers"},  
        "2-5": {"min": 2.0, "max": 5.0, "description": "Medium multipliers"},
        "5-10": {"min": 5.0, "max": 10.0, "description": "High multipliers"},
        "10-20": {"min": 10.0, "max": 20.0, "description": "Very high multipliers"},
        "20-50": {"min": 20.0, "max": 50.0, "description": "Extreme multipliers"},
        "50-100": {"min": 50.0, "max": 100.0, "description": "Ultra multipliers"},
        "100-200": {"min": 100.0, "max": 200.0, "description": "Mega multipliers"},
        "200-500": {"min": 200.0, "max": 500.0, "description": "Legendary multipliers"},
        "500-1000": {"min": 500.0, "max": 1000.0, "description": "Epic multipliers"},
        "1000-2000": {"min": 1000.0, "max": 2000.0, "description": "Mythic multipliers"},
        "2000-5000": {"min": 2000.0, "max": 5000.0, "description": "Maximum multipliers"},
        "5000+": {"min": 5000.0, "max": "unlimited", "description": "Beyond maximum"}
    }
    
    # Write stats file
    with open(stats_path, 'w') as f:
        json.dump(basic_stats, f, indent=2)
    
    return basic_stats


def analyze_multiplier_mode(config, mode_name, mode_cost):
    """
    Analyze statistics for a specific multiplier-based mode.
    
    Args:
        config: Game configuration
        mode_name: Name of the bet mode 
        mode_cost: Cost of the bet mode
        
    Returns:
        dict: Mode statistics
    """
    mode_stats = {
        "rtp_contribution": 0.0,
        "hit_rate": 0.0,
        "win_distribution": {},
        "multiplier_analysis": {}
    }
    
    force_data_loaded = False
    
    # Try to load force record data first (more accurate)
    force_path = os.path.join(config.library_path, "forces", f"force_record_{mode_name}.json")
    if os.path.exists(force_path):
        try:
            with open(force_path, 'r') as f:
                force_data = json.load(f)
                mode_stats.update(analyze_force_data(force_data, mode_cost))
                # Use the more accurate recalculation method
                mode_stats = recalculate_rtp_from_force_data(mode_stats, config, mode_name, mode_cost)
                force_data_loaded = True
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
    # Only try lookup table data if force data wasn't available
    if not force_data_loaded:
        lut_path = os.path.join(config.library_path, "publish_files", f"lookUpTable_{mode_name}_0.csv")
        if os.path.exists(lut_path):
            try:
                lut_stats = analyze_lookup_table(lut_path, mode_cost)
                mode_stats.update(lut_stats)
            except FileNotFoundError:
                pass
    
    return mode_stats


def analyze_force_data(force_data, mode_cost):
    """
    Analyze force record data for multiplier statistics.
    
    Args:
        force_data: Parsed force_record JSON data
        mode_cost: Bet mode cost
        
    Returns:
        dict: Force data analysis
    """
    stats = {
        "total_events": 0,
        "win_events": 0,
        "loss_events": 0,
        "multiplier_ranges": defaultdict(int)
    }
    
    total_sims = 0
    total_wins = 0
    
    for event in force_data:
        search_criteria_list = event.get("search", [])
        times_triggered = event.get("timesTriggered", 0)
        
        # Convert search criteria from list format to dict
        search_criteria = {}
        for item in search_criteria_list:
            search_criteria[item["name"]] = item["value"]
        
        stats["total_events"] += times_triggered
        total_sims += times_triggered
        
        symbol = search_criteria.get("symbol", "")
        kind = search_criteria.get("kind", "")
        
        if symbol == "multiplier":
            stats["win_events"] += times_triggered
            stats["multiplier_ranges"][kind] += times_triggered
            total_wins += times_triggered
        elif symbol == "loss":
            stats["loss_events"] += times_triggered
    
    # Calculate basic hit rates
    if total_sims > 0:
        win_rate = total_wins / total_sims
        loss_rate = stats["loss_events"] / total_sims
        stats["overall_hit_rate"] = round(win_rate, 4)
        stats["overall_hit_rate_percentage"] = f"{win_rate * 100:.1f}%"
        stats["loss_rate"] = round(loss_rate, 4)
        stats["loss_rate_percentage"] = f"{loss_rate * 100:.1f}%"
    
    return stats


def analyze_lookup_table(lut_path, mode_cost):
    """
    Analyze lookup table data for RTP and payout distribution.
    
    Args:
        lut_path: Path to lookup table CSV
        mode_cost: Bet mode cost
        
    Returns:
        dict: Lookup table analysis
    """
    stats = {
        "total_weight": 0,
        "total_payout": 0.0,
        "calculated_rtp": 0.0,
        "payout_distribution": defaultdict(int)
    }
    
    try:
        with open(lut_path, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    weight = int(parts[1])
                    payout_hundredths = int(parts[2])
                    multiplier = payout_hundredths / 100.0  # Convert from hundredths to multiplier
                    
                    stats["total_weight"] += weight
                    stats["total_payout"] += (multiplier * weight)  # Use actual multiplier
                    
                    # Categorize payouts using new range system
                    range_name = _get_payout_range(multiplier)
                    stats["payout_distribution"][range_name] += weight
        
        # Calculate RTP
        if stats["total_weight"] > 0:
            rtp_value = stats["total_payout"] / (stats["total_weight"] * mode_cost)
            stats["calculated_rtp"] = round(rtp_value, 4)
            stats["calculated_rtp_percentage"] = f"{rtp_value * 100:.2f}%"
    
    except (FileNotFoundError, ValueError):
        pass
    
    return stats


def _get_payout_range(multiplier):
    """
    Determine payout range for a given multiplier value.
    
    Args:
        multiplier: The multiplier value
        
    Returns:
        str: Range identifier
    """
    if multiplier <= 0:
        return "loss"
    elif 0 <= multiplier < 1:
        return "0-1"
    elif 1 <= multiplier < 2:
        return "1-2"
    elif 2 <= multiplier < 5:
        return "2-5"
    elif 5 <= multiplier < 10:
        return "5-10"
    elif 10 <= multiplier < 20:
        return "10-20"
    elif 20 <= multiplier < 50:
        return "20-50"
    elif 50 <= multiplier < 100:
        return "50-100"
    elif 100 <= multiplier < 200:
        return "100-200"
    elif 200 <= multiplier < 500:
        return "200-500"
    elif 500 <= multiplier < 1000:
        return "500-1000"
    elif 1000 <= multiplier < 2000:
        return "1000-2000"
    elif 2000 <= multiplier < 5000:
        return "2000-5000"
    elif multiplier >= 5000:
        return "5000+"
    else:
        return "other"


def recalculate_rtp_from_force_data(mode_stats, config, mode_name, mode_cost):
    """
    Recalculate RTP and payout distribution from current force data.
    
    Args:
        mode_stats: Current mode statistics
        config: Game configuration
        mode_name: Name of the bet mode
        mode_cost: Cost of the bet mode
        
    Returns:
        dict: Updated mode statistics with consistent data
    """
    force_path = os.path.join(config.library_path, "forces", f"force_record_{mode_name}.json")
    
    if not os.path.exists(force_path):
        return mode_stats
    
    try:
        with open(force_path, 'r') as f:
            force_data = json.load(f)
        
        total_payout = 0.0
        total_spins = 0
        updated_payout_distribution = defaultdict(int)
        
        for event in force_data:
            search_criteria_list = event.get("search", [])
            times_triggered = event.get("timesTriggered", 0)
            
            # Convert search criteria from list format to dict
            search_criteria = {}
            for item in search_criteria_list:
                search_criteria[item["name"]] = item["value"]
            
            symbol = search_criteria.get("symbol", "")
            kind = search_criteria.get("kind", "")
            win_amount = float(search_criteria.get("win_amount", 0.0))
            
            total_spins += times_triggered
            total_payout += (win_amount * times_triggered)
            
            # Update payout distribution based on current force data
            if symbol == "multiplier":
                updated_payout_distribution[kind] += times_triggered
            elif symbol == "loss":
                updated_payout_distribution["loss"] += times_triggered
        
        # Update mode stats with recalculated values
        if total_spins > 0:
            rtp_value = total_payout / (total_spins * mode_cost)
            mode_stats["calculated_rtp"] = round(rtp_value, 4)
            mode_stats["calculated_rtp_percentage"] = f"{rtp_value * 100:.2f}%"
            mode_stats["total_weight"] = total_spins
            mode_stats["total_payout"] = total_payout
            mode_stats["payout_distribution"] = dict(updated_payout_distribution)
    
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    return mode_stats