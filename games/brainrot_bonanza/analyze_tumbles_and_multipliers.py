#!/usr/bin/env python3
"""
Analyze tumbles and multipliers from Brainrot Bonanza books data.
Provides histograms and detailed breakdowns for base game and free game mechanics.
"""

import json
import os
import statistics
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple


def load_books_data(books_path: str) -> List[Dict]:
    """Load books data from JSON file."""
    with open(books_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_tumbles_in_spin(events: List[Dict]) -> Dict:
    """
    Analyze tumble data from a single spin/book's events.
    Returns detailed tumble information.
    """
    tumble_count = 0
    win_events = []
    tumble_wins = []
    total_win = 0

    for event in events:
        if event.get('type') == 'tumbleBoard':
            tumble_count += 1
        elif event.get('type') == 'winInfo':
            win_events.append(event)
            tumble_wins.append(event.get('totalWin', 0))
        elif event.get('type') == 'setTotalWin':
            total_win = event.get('amount', 0)

    return {
        'tumble_count': tumble_count,
        'win_events': len(win_events),
        'tumble_wins': tumble_wins,
        'total_win': total_win,
        'avg_win_per_tumble': statistics.mean(tumble_wins) if tumble_wins else 0
    }

def analyze_multipliers_in_spin(events: List[Dict]) -> Dict:
    """
    Analyze multiplier data from a single free spin's events.
    Returns detailed multiplier information.
    """
    multiplier_info = {
        'has_multipliers': False,
        'multiplier_positions': [],
        'multiplier_values': [],
        'multiplier_sum': 0,
        'tumble_win_before_mult': 0,
        'total_win_after_mult': 0,
        'multiplier_factor': 1.0
    }

    for event in events:
        if event.get('type') == 'boardMultiplierInfo':
            multiplier_info['has_multipliers'] = True

            # Extract multiplier positions and values
            mult_info = event.get('multInfo', {})
            positions = mult_info.get('positions', [])

            for pos in positions:
                multiplier_info['multiplier_positions'].append({
                    'reel': pos.get('reel'),
                    'row': pos.get('row'),
                    'value': pos.get('multiplier')
                })
                multiplier_info['multiplier_values'].append(pos.get('multiplier', 0))

            # Extract win calculation
            win_info = event.get('winInfo', {})
            multiplier_info['tumble_win_before_mult'] = win_info.get('tumbleWin', 0)
            multiplier_info['total_win_after_mult'] = win_info.get('totalWin', 0)
            multiplier_info['multiplier_sum'] = win_info.get('boardMult', 0)

            if multiplier_info['tumble_win_before_mult'] > 0:
                multiplier_info['multiplier_factor'] = (
                    multiplier_info['total_win_after_mult'] / multiplier_info['tumble_win_before_mult']
                )

            break

    return multiplier_info

def create_text_histograms(data: Dict):
    """Create text-based histograms for tumble and multiplier analysis."""

    def print_histogram(title, counter_data, max_bars=50):
        """Print a simple text histogram."""
        print(f"\n{title}")
        print("=" * len(title))

        if not counter_data:
            print("No data available")
            return

        max_count = max(counter_data.values()) if counter_data else 0
        if max_count == 0:
            print("No data available")
            return

        for value in sorted(counter_data.keys()):
            count = counter_data[value]
            bar_length = int((count / max_count) * max_bars)
            bar = "#" * bar_length
            pct = (count / sum(counter_data.values())) * 100
            print(f"{value:3}: {count:6} ({pct:5.1f}%) {bar}")

    # 1. Base Game Tumbles per Spin
    if data['base_tumbles_per_spin']:
        base_tumble_counter = Counter(data['base_tumbles_per_spin'])
        print_histogram("BASE GAME: Tumbles per Spin Distribution", base_tumble_counter)

    # 2. Free Game Tumbles per Individual Free Spin
    if data['free_tumbles_per_individual_spin']:
        free_tumble_counter = Counter(data['free_tumbles_per_individual_spin'])
        print_histogram("FREE GAME: Tumbles per Individual Free Spin Distribution", free_tumble_counter)

    # 3. Free Game Tumbles per Entire Bonus Round
    if data['free_tumbles_per_bonus']:
        # Group into ranges for readability
        bonus_tumble_ranges = Counter()
        for tumbles in data['free_tumbles_per_bonus']:
            range_key = f"{(tumbles // 5) * 5}-{(tumbles // 5) * 5 + 4}"
            bonus_tumble_ranges[range_key] += 1
        print_histogram("FREE GAME: Total Tumbles per Bonus Round Distribution (Grouped by 5s)", bonus_tumble_ranges)

    # 4. Multiplier Values Distribution
    if data['multiplier_values']:
        mult_value_counter = Counter(data['multiplier_values'])
        print_histogram("MULTIPLIER VALUES: Individual M Symbol Distribution", mult_value_counter)

    # 5. Multiplier Sums per Free Spin
    if data['multiplier_sums_per_spin']:
        # Group into ranges for readability
        mult_sum_ranges = Counter()
        for mult_sum in data['multiplier_sums_per_spin']:
            range_key = f"{int(mult_sum // 5) * 5}-{int(mult_sum // 5) * 5 + 4}"
            mult_sum_ranges[range_key] += 1
        print_histogram("MULTIPLIER SUMS: Total per Free Spin Distribution (Grouped by 5s)", mult_sum_ranges)

def analyze_all_books(books_data: List[Dict], game_mode: str) -> Dict:
    """
    Analyze all books for tumbles and multipliers.
    Returns comprehensive analysis data.
    """

    # Separate base game and free game books
    base_books = []
    free_books = []

    for book in books_data:
        criteria = book.get('criteria', '')
        if criteria in ['0', 'basegame']:
            base_books.append(book)
        elif criteria == 'freegame':
            free_books.append(book)

    analysis_data = {
        'total_books': len(books_data),
        'base_books': len(base_books),
        'free_books': len(free_books),
        'game_mode': game_mode,

        # Base game tumble data (per spin)
        'base_tumbles_per_spin': [],
        'base_total_wins': [],

        # Free game tumble data (per individual free spin)
        'free_tumbles_per_individual_spin': [],
        'free_tumbles_per_bonus': [],  # Total tumbles for entire bonus round

        # Multiplier data (free game only)
        'multiplier_values': [],  # Individual M symbol values (used multipliers only)
        'multiplier_values_landed': [],  # All M symbols that land (whether used or not)
        'multiplier_sums_per_spin': [],  # Sum of multipliers per free spin (when present)
        'multiplier_frequency': 0,  # % of free spins with multipliers used
        'multiplier_land_frequency': 0,  # % of free spins with multipliers landed
        'multiplier_win_impact': [],  # Multiplier factor applied to wins
        'spins_with_landed_mult': 0,
        'retrigger_counts': [],  # Number of retriggers per bonus
        'retrigger_amounts': [],  # Amount of free spins awarded per retrigger

        # Detailed breakdowns
        'base_tumble_breakdown': Counter(),
        'free_tumble_breakdown': Counter(),
        'multiplier_value_breakdown': Counter(),
        'multiplier_landed_breakdown': Counter(),
    }

    # Analyze base game books
    for book in base_books:
        events = book.get('events', [])
        tumble_analysis = analyze_tumbles_in_spin(events)

        analysis_data['base_tumbles_per_spin'].append(tumble_analysis['tumble_count'])
        analysis_data['base_total_wins'].append(tumble_analysis['total_win'])
        analysis_data['base_tumble_breakdown'][tumble_analysis['tumble_count']] += 1

    # Analyze free game books
    # Note: Each free game "book" contains multiple individual free spins
    for book in free_books:
        events = book.get('events', [])

        # Count total tumbles for entire bonus
        total_bonus_tumbles = 0
        individual_spin_tumbles = []
        current_spin_tumbles = 0

        # Track multipliers
        bonus_multiplier_values = []  # Only multipliers that were used (from boardMultiplierInfo)
        bonus_multiplier_sums = []
        spins_with_multipliers = 0

        # Track ALL multipliers that land (whether used or not)
        bonus_multiplier_values_landed = []  # All M symbols that land (from multiplierLanded)
        current_spin_has_landed_mult = False  # Track if current spin has landed multipliers

        # Track retriggers
        retrigger_count = 0
        retrigger_amounts = []

        # Simply count reveals in free spin books (first reveal is base game trigger)
        reveal_count = 0
        free_spin_count = 0

        for event in events:
            if event.get('type') == 'reveal':
                reveal_count += 1

                # Skip the first reveal which is the base game trigger
                if reveal_count == 1:
                    current_spin_tumbles = 0
                    current_spin_has_landed_mult = False
                    continue

                # This is a free spin
                free_spin_count += 1

                # Save previous spin's tumbles (for spins after the first free spin)
                if free_spin_count > 1:
                    individual_spin_tumbles.append(current_spin_tumbles)
                    analysis_data['free_tumble_breakdown'][current_spin_tumbles] += 1

                    # Count spin with multipliers if any landed during the previous spin
                    if current_spin_has_landed_mult:
                        analysis_data['spins_with_landed_mult'] += 1

                current_spin_tumbles = 0
                current_spin_has_landed_mult = False  # Reset for new spin

            elif event.get('type') == 'tumbleBoard':
                current_spin_tumbles += 1
                total_bonus_tumbles += 1

            # Count M symbols from reveal events (after first one)
            if event.get('type') == 'reveal' and reveal_count > 1:
                board = event.get('board', [])
                for reel in board:
                    for symbol in reel:
                        if symbol.get('name') == 'M':
                            mult_value = symbol.get('multiplier', 0)
                            if mult_value > 0:
                                bonus_multiplier_values_landed.append(mult_value)
                                current_spin_has_landed_mult = True

            # Also count M symbols from tumbleBoard new symbols
            elif event.get('type') == 'tumbleBoard':
                new_symbols = event.get('newSymbols', [])
                for reel_symbols in new_symbols:
                    for symbol in reel_symbols:
                        if symbol.get('name') == 'M':
                            mult_value = symbol.get('multiplier', 0)
                            if mult_value > 0:
                                bonus_multiplier_values_landed.append(mult_value)
                                current_spin_has_landed_mult = True

            elif event.get('type') == 'freeSpinRetrigger':
                # This is an actual retrigger during free spins
                retrigger_count += 1
                # Math spec: 3+ scatters → +5 spins during free games
                retrigger_amounts.append(5)  # Fixed +5 FS per retrigger

            elif event.get('type') == 'boardMultiplierInfo':
                # Multiplier collection event
                mult_info = event.get('multInfo', {})
                positions = mult_info.get('positions', [])

                spin_multiplier_sum = 0
                for pos in positions:
                    mult_value = pos.get('multiplier', 0)
                    bonus_multiplier_values.append(mult_value)
                    spin_multiplier_sum += mult_value

                if spin_multiplier_sum > 0:
                    bonus_multiplier_sums.append(spin_multiplier_sum)
                    spins_with_multipliers += 1

                    # Track multiplier impact
                    win_info = event.get('winInfo', {})
                    tumble_win = win_info.get('tumbleWin', 0)
                    total_win = win_info.get('totalWin', 0)
                    if tumble_win > 0:
                        impact_factor = total_win / tumble_win
                        analysis_data['multiplier_win_impact'].append(impact_factor)

        # Add final spin's tumbles if we had any free spins
        if free_spin_count > 0:
            individual_spin_tumbles.append(current_spin_tumbles)
            analysis_data['free_tumble_breakdown'][current_spin_tumbles] += 1

            # Count final spin with multipliers if any landed
            if current_spin_has_landed_mult:
                analysis_data['spins_with_landed_mult'] += 1

        # Store data
        analysis_data['free_tumbles_per_bonus'].append(total_bonus_tumbles)
        analysis_data['free_tumbles_per_individual_spin'].extend(individual_spin_tumbles)
        analysis_data['multiplier_values'].extend(bonus_multiplier_values)  # Used multipliers
        analysis_data['multiplier_values_landed'].extend(bonus_multiplier_values_landed)  # All landed multipliers
        analysis_data['multiplier_sums_per_spin'].extend(bonus_multiplier_sums)
        analysis_data['retrigger_counts'].append(retrigger_count)
        analysis_data['retrigger_amounts'].extend(retrigger_amounts)

        # Count multiplier value occurrences (used vs landed)
        for value in bonus_multiplier_values:
            analysis_data['multiplier_value_breakdown'][value] += 1
        for value in bonus_multiplier_values_landed:
            analysis_data['multiplier_landed_breakdown'][value] += 1

    # Calculate multiplier frequencies
    total_free_spins = len(analysis_data['free_tumbles_per_individual_spin'])
    total_bonuses = len(analysis_data['free_tumbles_per_bonus'])

    if total_free_spins > 0:
        analysis_data['multiplier_frequency'] = (len(analysis_data['multiplier_sums_per_spin']) / total_free_spins) * 100
        analysis_data['multiplier_land_frequency'] = (analysis_data['spins_with_landed_mult'] / total_free_spins) * 100

    # Calculate multipliers per bonus and per free spin
    if len(analysis_data['multiplier_values_landed']) > 0:
        analysis_data['avg_multipliers_per_bonus'] = len(analysis_data['multiplier_values_landed']) / total_bonuses if total_bonuses > 0 else 0
        analysis_data['avg_multipliers_per_freespin'] = len(analysis_data['multiplier_values_landed']) / total_free_spins if total_free_spins > 0 else 0

    return analysis_data

def print_detailed_analysis(data: Dict):
    """Print comprehensive analysis results."""

    print(f"\n{'='*80}")
    print(f"BRAINROT BONANZA TUMBLE & MULTIPLIER ANALYSIS - {data['game_mode'].upper()}")
    print(f"{'='*80}")

    print(f"\nDATASET SUMMARY")
    print(f"   Total books analyzed: {data['total_books']:,}")
    print(f"   Base game books: {data['base_books']:,}")
    print(f"   Free game books: {data['free_books']:,}")
    print(f"   Total individual free spins: {len(data['free_tumbles_per_individual_spin']):,}")

    # Base Game Tumble Analysis
    if data['base_tumbles_per_spin']:
        print(f"\nBASE GAME TUMBLES (Per Individual Spin)")
        print(f"   Average tumbles per spin: {statistics.mean(data['base_tumbles_per_spin']):.2f}")
        print(f"   Median tumbles per spin: {statistics.median(data['base_tumbles_per_spin']):.2f}")
        print(f"   Max tumbles in a spin: {max(data['base_tumbles_per_spin'])}")
        print(f"   Spins with no tumbles: {data['base_tumbles_per_spin'].count(0):,} ({(data['base_tumbles_per_spin'].count(0) / len(data['base_tumbles_per_spin'])) * 100:.1f}%)")
        print(f"   Spins with 1+ tumbles: {len([x for x in data['base_tumbles_per_spin'] if x > 0]):,} ({(len([x for x in data['base_tumbles_per_spin'] if x > 0]) / len(data['base_tumbles_per_spin'])) * 100:.1f}%)")

        print(f"\n   Tumble Distribution (Base Game):")
        for tumbles in sorted(data['base_tumble_breakdown'].keys()):
            count = data['base_tumble_breakdown'][tumbles]
            pct = (count / len(data['base_tumbles_per_spin'])) * 100
            print(f"     {tumbles} tumbles: {count:,} spins ({pct:.1f}%)")

    # Free Game Tumble Analysis
    if data['free_tumbles_per_individual_spin']:
        print(f"\nFREE GAME TUMBLES (Per Individual Free Spin)")
        print(f"   Average tumbles per FS: {statistics.mean(data['free_tumbles_per_individual_spin']):.2f}")
        print(f"   Median tumbles per FS: {statistics.median(data['free_tumbles_per_individual_spin']):.2f}")
        print(f"   Max tumbles in a FS: {max(data['free_tumbles_per_individual_spin'])}")
        print(f"   FS with no tumbles: {data['free_tumbles_per_individual_spin'].count(0):,} ({(data['free_tumbles_per_individual_spin'].count(0) / len(data['free_tumbles_per_individual_spin'])) * 100:.1f}%)")
        print(f"   FS with 1+ tumbles: {len([x for x in data['free_tumbles_per_individual_spin'] if x > 0]):,} ({(len([x for x in data['free_tumbles_per_individual_spin'] if x > 0]) / len(data['free_tumbles_per_individual_spin'])) * 100:.1f}%)")

        print(f"\n   Tumble Distribution (Free Spins):")
        for tumbles in sorted(data['free_tumble_breakdown'].keys())[:10]:  # Show top 10
            count = data['free_tumble_breakdown'][tumbles]
            pct = (count / len(data['free_tumbles_per_individual_spin'])) * 100
            print(f"     {tumbles} tumbles: {count:,} FS ({pct:.1f}%)")

        if data['free_tumbles_per_bonus']:
            print(f"\nFREE GAME TUMBLES (Per Entire Bonus Round)")
            print(f"   Average tumbles per bonus: {statistics.mean(data['free_tumbles_per_bonus']):.1f}")
            print(f"   Median tumbles per bonus: {statistics.median(data['free_tumbles_per_bonus']):.1f}")
            print(f"   Max tumbles in a bonus: {max(data['free_tumbles_per_bonus'])}")

    # Multiplier Analysis
    if data['multiplier_values_landed']:
        print(f"\nMULTIPLIER ANALYSIS (Free Spins Only)")
        print(f"   Total M symbols that landed: {len(data['multiplier_values_landed']):,}")
        print(f"   Total M symbols that were used: {len(data['multiplier_values']):,}")
        print(f"   Average M symbol value (landed): {statistics.mean(data['multiplier_values_landed']):.1f}x")
        print(f"   Median M symbol value (landed): {statistics.median(data['multiplier_values_landed']):.1f}x")
        print(f"   Multiplier land frequency: {data['multiplier_land_frequency']:.1f}% of free spins have M symbols")
        print(f"   Multiplier use frequency: {data['multiplier_frequency']:.1f}% of free spins use multipliers")

        usage_rate = (len(data['multiplier_values']) / len(data['multiplier_values_landed'])) * 100 if data['multiplier_values_landed'] else 0
        print(f"   Multiplier usage rate: {usage_rate:.1f}% of landed M symbols get used")

        print(f"\n   Multiplier Value Distribution (All Landed):")
        for value in sorted(data['multiplier_landed_breakdown'].keys()):
            count = data['multiplier_landed_breakdown'][value]
            pct = (count / len(data['multiplier_values_landed'])) * 100
            print(f"     {value}x: {count:,} symbols ({pct:.1f}%)")

        if data['multiplier_sums_per_spin']:
            print(f"\n   Multiplier Sums (When Used):")
            print(f"     Average sum per FS: {statistics.mean(data['multiplier_sums_per_spin']):.1f}x")
            print(f"     Median sum per FS: {statistics.median(data['multiplier_sums_per_spin']):.1f}x")
            print(f"     Max sum in a FS: {max(data['multiplier_sums_per_spin']):.1f}x")
            print(f"     Min sum in a FS: {min(data['multiplier_sums_per_spin']):.1f}x")

        if data['multiplier_win_impact']:
            print(f"\n   Multiplier Win Impact:")
            print(f"     Average multiplier factor: {statistics.mean(data['multiplier_win_impact']):.1f}x")
            print(f"     Median multiplier factor: {statistics.median(data['multiplier_win_impact']):.1f}x")
            print(f"     Max multiplier factor: {max(data['multiplier_win_impact']):.1f}x")

    # Retrigger Analysis
    if data['retrigger_counts']:
        print(f"\nRETRIGGER ANALYSIS (Free Spins Only)")
        total_bonuses = len(data['retrigger_counts'])
        bonuses_with_retriggers = len([x for x in data['retrigger_counts'] if x > 0])
        print(f"   Total bonus rounds: {total_bonuses:,}")
        print(f"   Bonuses with retriggers: {bonuses_with_retriggers:,} ({(bonuses_with_retriggers / total_bonuses) * 100:.1f}%)")
        print(f"   Average retriggers per bonus: {statistics.mean(data['retrigger_counts']):.2f}")

        if data['retrigger_amounts']:
            total_retrigger_spins = sum(data['retrigger_amounts'])
            print(f"   Total free spins from retriggers: {total_retrigger_spins:,}")
            print(f"   Average FS per retrigger: {statistics.mean(data['retrigger_amounts']):.1f}")

            retrigger_breakdown = Counter(data['retrigger_counts'])
            print(f"\n   Retrigger Distribution:")
            for retriggers in sorted(retrigger_breakdown.keys())[:10]:
                count = retrigger_breakdown[retriggers]
                pct = (count / total_bonuses) * 100
                print(f"     {retriggers} retriggers: {count:,} bonuses ({pct:.1f}%)")

    # Multiplier Statistics
    if 'avg_multipliers_per_bonus' in data:
        print(f"\nMULTIPLIER STATISTICS (Free Spins Only)")
        print(f"   Total multipliers landed: {len(data['multiplier_values_landed']):,}")
        print(f"   Average multipliers per bonus: {data['avg_multipliers_per_bonus']:.2f}")
        print(f"   Average multipliers per free spin: {data['avg_multipliers_per_freespin']:.3f}")

        if 'multiplier_land_frequency' in data:
            print(f"   Free spins with 1+ multipliers: {data['spins_with_landed_mult']:,} ({data['multiplier_land_frequency']:.1f}%)")

def main():
    """Main analysis function."""

    base_path = "C:\\Users\\jonah\\math-sdk-1\\games\\brainrot_bonanza\\library\\books"
    output_dir = "C:\\Users\\jonah\\math-sdk-1\\games\\brainrot_bonanza\\analysis_output"

    # Analyze base mode
    base_books_path = os.path.join(base_path, "books_base.json")
    if os.path.exists(base_books_path):
        print("Loading base game books...")
        base_books = load_books_data(base_books_path)
        base_analysis = analyze_all_books(base_books, "BASE")
        print_detailed_analysis(base_analysis)

        print(f"\nCreating histograms for BASE mode...")
        create_text_histograms(base_analysis)

    # Analyze bonus mode
    bonus_books_path = os.path.join(base_path, "books_bonus.json")
    if os.path.exists(bonus_books_path):
        print(f"\n{'='*80}")
        print("Loading bonus game books...")
        bonus_books = load_books_data(bonus_books_path)
        bonus_analysis = analyze_all_books(bonus_books, "BONUS")
        print_detailed_analysis(bonus_analysis)

        print(f"\nCreating histograms for BONUS mode...")
        create_text_histograms(bonus_analysis)

    print(f"\n{'='*80}")
    print(f"Analysis complete! Histograms saved to: {output_dir}")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()