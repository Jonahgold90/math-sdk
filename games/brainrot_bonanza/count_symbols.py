#!/usr/bin/env python3
"""
Count all symbols in BR0.csv and FR0.csv reel files.
Quick analysis tool for symbol distribution verification.
"""

import csv
from collections import Counter
import os

def count_symbols_in_reel(filename):
    """Count all symbols in a reel CSV file."""
    if not os.path.exists(filename):
        print(f"Error: {filename} not found!")
        return Counter()

    all_symbols = []
    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            all_symbols.extend(row)

    return Counter(all_symbols)

def print_symbol_counts(counts, reel_name):
    """Print symbol counts in a formatted way."""
    print(f"\n=== {reel_name} SYMBOL COUNTS ===")

    # Separate symbol types
    high_pays = {}
    low_pays = {}
    special = {}

    for symbol, count in counts.items():
        if symbol.startswith('H'):
            high_pays[symbol] = count
        elif symbol.startswith('L'):
            low_pays[symbol] = count
        elif symbol in ['S', 'M']:
            special[symbol] = count

    # Print high pays
    print("High Pays:")
    for symbol in sorted(high_pays.keys()):
        print(f"  {symbol}: {high_pays[symbol]}")

    # Print low pays
    print("Low Pays:")
    for symbol in sorted(low_pays.keys()):
        print(f"  {symbol}: {low_pays[symbol]}")

    # Print special symbols
    if special:
        print("Special Symbols:")
        for symbol in sorted(special.keys()):
            print(f"  {symbol}: {special[symbol]}")

    print(f"Total symbols: {sum(counts.values())}")

def main():
    """Count symbols in both reel files."""
    reel_files = {
        "reels/BR0.csv": "BASE GAME (BR0)",
        "reels/FR0.csv": "FREE GAME (FR0)"
    }

    for filename, reel_name in reel_files.items():
        counts = count_symbols_in_reel(filename)
        print_symbol_counts(counts, reel_name)

    # Quick verification
    print("\n=== QUICK VERIFICATION ===")

    # Check BR0
    br0_counts = count_symbols_in_reel("reels/BR0.csv")
    if br0_counts:
        print("BR0 - Low pay order check (should be L5 > L4 > L3 > L2 > L1):")
        low_symbols = ['L5', 'L4', 'L3', 'L2', 'L1']
        for symbol in low_symbols:
            if symbol in br0_counts:
                print(f"  {symbol}: {br0_counts[symbol]}")

        if 'L1' in br0_counts and 'H1' in br0_counts:
            l1_gt_h1 = br0_counts['L1'] > br0_counts['H1']
            print(f"  L1 > H1: {br0_counts['L1']} > {br0_counts['H1']} = {'PASS' if l1_gt_h1 else 'FAIL'}")

    # Check FR0
    fr0_counts = count_symbols_in_reel("reels/FR0.csv")
    if fr0_counts:
        print("\nFR0 - Special symbols:")
        if 'S' in fr0_counts:
            print(f"  Scatters (S): {fr0_counts['S']}")
        if 'M' in fr0_counts:
            print(f"  Multipliers (M): {fr0_counts['M']}")

if __name__ == "__main__":
    main()