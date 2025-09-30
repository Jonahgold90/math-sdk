#!/usr/bin/env python3
"""
Generate reel strips for Brainrot Bonanza game based on weighted symbol distribution.
Creates BR0.csv (base game) and FR0.csv (free game) with proper symbol frequencies.
"""

import random
import csv
from collections import Counter

def generate_reel_strip(symbol_weights, num_reels=6, target_length=250):
    """
    Generate a single reel strip based on symbol weights.

    Args:
        symbol_weights: Dict of {symbol: weight} pairs
        num_reels: Number of reels (columns)
        target_length: Target number of rows

    Returns:
        List of lists representing the reel strip
    """
    symbols = list(symbol_weights.keys())
    weights = list(symbol_weights.values())

    # Generate the reel strip
    reel_data = []

    for row in range(target_length):
        reel_row = []
        for reel in range(num_reels):
            # Add some variation per reel to avoid identical columns
            seed = (row * num_reels + reel) % 1000
            random.seed(seed)
            symbol = random.choices(symbols, weights=weights)[0]
            reel_row.append(symbol)
        reel_data.append(reel_row)

    return reel_data

def save_reel_to_csv(reel_data, filename):
    """Save reel data to CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for row in reel_data:
            writer.writerow(row)

def count_symbols(reel_data):
    """Count total occurrences of each symbol in the reel."""
    all_symbols = []
    for row in reel_data:
        all_symbols.extend(row)
    return Counter(all_symbols)

def main():
    """Generate both base game and free game reel strips."""

    # Base game symbol weights (BR0.csv)
    # Higher weights = more frequent
    base_weights = {
    'H1': 44, 'H2': 54, 'H3': 64, 'H4': 74,
    'L1': 94, 'L2': 108, 'L3': 118, 'L4': 142,   # L5 removed
    'S': 21,  # ≈44/1500 scatters → ~1.0–1.1% FS triggers (tweak 20–22 to taste)
    }



    # Free game symbol weights (FR0.csv)
    # Similar distribution but with multipliers
    free_weights = {
    'H1': 42, 'H2': 51, 'H3': 61, 'H4': 71,
    'L1': 90, 'L2': 102, 'L3': 116, 'L4': 150,  # L4 becomes the “cheapest” & most frequent
    'S': 15,                                    # ≈30–33/1500 for retriggers
    'M': 15.2,                                  # ≈36 bombs of 1500 → ~0.72 bombs/drop
    }



    print("Generating base game reel strip (BR0.csv)...")
    base_reel = generate_reel_strip(base_weights, num_reels=6, target_length=250)
    save_reel_to_csv(base_reel, 'BR0.csv')

    print("Generating free game reel strip (FR0.csv)...")
    free_reel = generate_reel_strip(free_weights, num_reels=6, target_length=250)
    save_reel_to_csv(free_reel, 'FR0.csv')

    # Print symbol distribution for verification
    print("\n=== BASE GAME (BR0) SYMBOL DISTRIBUTION ===")
    base_counts = count_symbols(base_reel)
    for symbol in sorted(base_counts.keys()):
        print(f"{symbol}: {base_counts[symbol]}")

    print(f"\nTotal symbols: {sum(base_counts.values())}")

    print("\n=== FREE GAME (FR0) SYMBOL DISTRIBUTION ===")
    free_counts = count_symbols(free_reel)
    for symbol in sorted(free_counts.keys()):
        print(f"{symbol}: {free_counts[symbol]}")

    print(f"\nTotal symbols: {sum(free_counts.values())}")

    # Verify distribution order
    print("\n=== DISTRIBUTION VERIFICATION ===")
    print("Base game low pay order (should be L5 > L4 > L3 > L2 > L1):")
    low_pays = ['L5', 'L4', 'L3', 'L2', 'L1']
    for symbol in low_pays:
        if symbol in base_counts:
            print(f"  {symbol}: {base_counts[symbol]}")

    print("\nBase game should have L1 > H1:")
    if 'L1' in base_counts and 'H1' in base_counts:
        print(f"  L1: {base_counts['L1']}, H1: {base_counts['H1']} -> {'PASS' if base_counts['L1'] > base_counts['H1'] else 'FAIL'}")

if __name__ == "__main__":
    main()