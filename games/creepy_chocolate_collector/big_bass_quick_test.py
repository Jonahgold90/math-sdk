"""
Quick test of Big Bass mechanics without formatting issues
"""

import json
import zstandard as zstd
import os
from collections import defaultdict, Counter

def load_books(file_path):
    with open(file_path, 'rb') as f:
        dctx = zstd.ZstdDecompressor()
        with dctx.stream_reader(f) as reader:
            decompressed = reader.read()
            lines = decompressed.decode('utf-8').strip().split('\n')
            return [json.loads(line) for line in lines if line.strip()]

def extract_board_symbols(board):
    symbols = []
    for row in board:
        for cell in row:
            symbols.append(cell['name'])
    return symbols

def calculate_collection_value(cc_values, cw_count, level_multiplier):
    """Calculate collection value using Big Bass formula"""
    if not cc_values or cw_count == 0:
        return 0
    
    cc_sum = sum(cc_values)
    return cc_sum * cw_count * level_multiplier

def extract_cc_values(board, event=None):
    """Extract actual CC values from cash_value attribute - NO FALLBACKS"""
    cc_values = []
    
    for row_idx, row in enumerate(board):
        for col_idx, cell in enumerate(row):
            if cell['name'] == 'CC':
                # Only use real cash_value - no fallbacks to ensure data accuracy
                cash_value = cell.get('cash_value')
                if cash_value is not None:
                    cc_values.append(cash_value)
                # If cash_value is missing, we skip this CC symbol entirely
    
    return cc_values

def analyze_collector_mechanics(books):
    analysis = {
        'bonus_rounds': 0,
        'total_bonus_spins': 0,
        'cw_events': defaultdict(int),
        'cc_events': defaultdict(int),
        'collection_events': [],
        'dead_cws': 0,
        'orphan_chocolates': 0,
        'cw_cc_co_occurrence': 0,
        
        # New detailed stats
        'cw_per_bonus': [],  # List of CW counts per bonus
        'cc_per_bonus': [],  # List of CC counts per bonus  
        'collections_per_bonus': [],  # List of collection event counts per bonus
        'levels_reached': [],  # List of max level reached per bonus
        'collected_values': [],  # List of individual collected values
        'dead_spin_streaks': [],  # List of dead spin streak lengths
        'cc_per_spin_distribution': defaultdict(int),  # CC count per individual spin
        'cw_collected': 0,  # CW symbols that participated in collections
        'cw_dead': 0,  # CW symbols that didn't collect anything

    }
    spins_with_cw = 0
    spins_with_cc = 0
    
        # 🔹 Initialize headline counters here

    for book in books:
        if not book.get('events'):
            continue
            
        has_reveals = any(event.get('type') == 'reveal' for event in book['events'])
        if not has_reveals:
            continue
            
        analysis['bonus_rounds'] += 1
        spin_count = 0
        
        # Per-bonus tracking
        cw_count_this_bonus = 0
        cc_count_this_bonus = 0
        collections_this_bonus = 0
        level_this_bonus = 1
        dead_spin_streak = 0
        
        events = book['events']
        reveal_events = [(i, event) for i, event in enumerate(events) if event.get('type') == 'reveal']
        
        for reveal_index, event in reveal_events:
            spin_count += 1
            analysis['total_bonus_spins'] += 1
            
            board = event.get('board', [])
            symbols = extract_board_symbols(board)
            cc_values = extract_cc_values(board, event)
            
            cw_on_board = sum(1 for s in symbols if s == 'CW')
            cc_on_board = sum(1 for s in symbols if s == 'CC')
            
            if cw_on_board > 0:
                spins_with_cw += 1
            if cc_on_board > 0:
                spins_with_cc += 1


            # Track CC per spin distribution
            analysis['cc_per_spin_distribution'][cc_on_board] += 1
            
            # Track totals for this bonus
            cw_count_this_bonus += cw_on_board
            cc_count_this_bonus += cc_on_board
            
            if cw_on_board > 0:
                analysis['cw_events'][cw_on_board] += 1
            
            if cc_on_board > 0:
                analysis['cc_events'][cc_on_board] += 1
            
            # Level progression (every 4 CWs) - triggers on any CW appearance
            # Level progression (every 4 CWs) — count ANY CWs, even if no CCs
            if cw_on_board > 0:
                # Update level based on total CWs accumulated so far (including this spin)
                total_cws_so_far = cw_count_this_bonus
                if total_cws_so_far >= 12:
                    level_this_bonus = 4
                elif total_cws_so_far >= 8:
                    level_this_bonus = 3
                elif total_cws_so_far >= 4:
                    level_this_bonus = 2
                else:
                    level_this_bonus = 1

            
            if cw_on_board > 0 and cc_on_board > 0:
                # This is a collection event - CW + CC always collect
                analysis['cw_cc_co_occurrence'] += 1
                collections_this_bonus += 1
                
                # Record dead streak before resetting
                if dead_spin_streak > 0:
                    analysis['dead_spin_streaks'].append(dead_spin_streak)
                dead_spin_streak = 0  # Reset dead streak
                
                # Calculate collection value using Big Bass formula
                collected_value = calculate_collection_value(cc_values, cw_on_board, level_this_bonus)
                
                analysis['collected_values'].append(collected_value)
                
                analysis['collection_events'].append({
                    'bonus_id': book['id'],
                    'spin': spin_count,
                    'cw_count': cw_on_board,
                    'cc_count': cc_on_board,
                    'level': level_this_bonus,
                    'collected_value': collected_value,
                    'cc_values': cc_values,
                    'cc_sum': sum(cc_values) if cc_values else 0,
                })
                
                # Track collected CWs (all CWs in CW+CC co-occurrence collect)
                analysis['cw_collected'] += cw_on_board
                    
            elif cw_on_board > 0 and cc_on_board == 0:
                analysis['dead_cws'] += cw_on_board
                analysis['cw_dead'] += cw_on_board
                dead_spin_streak += 1
                
            elif cw_on_board == 0 and cc_on_board > 0:
                analysis['orphan_chocolates'] += cc_on_board
                dead_spin_streak += 1
            else:
                # Neither CW nor CC
                dead_spin_streak += 1
                
        # Record per-bonus stats
        analysis['cw_per_bonus'].append(cw_count_this_bonus)
        analysis['cc_per_bonus'].append(cc_count_this_bonus)
        analysis['collections_per_bonus'].append(collections_this_bonus)
        analysis['levels_reached'].append(level_this_bonus)
        if dead_spin_streak > 0:
            analysis['dead_spin_streaks'].append(dead_spin_streak)

    analysis['spins_with_cw'] = spins_with_cw
    analysis['spins_with_cc'] = spins_with_cc
    return analysis

def main():
    books_path = os.path.join("library", "publish_files", "books_bonus.jsonl.zst")
    books = load_books(books_path)
    print(f"Loaded {len(books)} bonus rounds")
    
    analysis = analyze_collector_mechanics(books)
    
    print(f"\nBONUS ROUND SUMMARY:")
    print(f"  Total Bonus Rounds: {analysis['bonus_rounds']:,}")
    print(f"  Total Bonus Spins: {analysis['total_bonus_spins']:,}")
    
    total_cws = sum(k * v for k, v in analysis['cw_events'].items())
    total_ccs = sum(k * v for k, v in analysis['cc_events'].items())
    
    print(f"\nCOLLECTOR WILD ANALYSIS:")
    print(f"  Total CW Events: {total_cws:,}")
    print(f"  CWs that collected: {analysis['cw_collected']:,}")
    print(f"  Dead CWs (no CC): {analysis['cw_dead']:,}")
    if total_cws > 0:
        collection_rate = analysis['cw_collected'] / total_cws * 100
        print(f"  CW collection rate: {collection_rate:.1f}%")
    
    print(f"\nCHOCOLATE CASH ANALYSIS:")
    print(f"  Total CC Events: {total_ccs:,}")
    print(f"  Orphan Chocolates (no CW): {analysis['orphan_chocolates']}")
    
    print(f"\nCOLLECTION MECHANICS:")
    print(f"  Total Collection Events: {len(analysis['collection_events'])}")
    print(f"  CW-CC Co-occurrence: {analysis['cw_cc_co_occurrence']} events")
    
    if analysis['collection_events']:
        print(f"\nSAMPLE COLLECTION EVENTS:")
        print(f"  All values calculated using Big Bass formula: CC_sum × CW_count × Level")
        
        # Enhanced sample display
        for i, event in enumerate(analysis['collection_events'][:5]):
            cc_sum = event.get('cc_sum', 0)
            formula_result = cc_sum * event['cw_count'] * event['level']
            cc_info = f" (CC values: {event['cc_values']}, sum={cc_sum})"
            print(f"  Event {i+1}: {event['cw_count']} CW + {event['cc_count']} CC at Level {event['level']} = {event['collected_value']} value{cc_info} (Bonus {event['bonus_id']}, Spin {event['spin']})")
            print(f"    Formula: {cc_sum} × {event['cw_count']} × {event['level']} = {formula_result}")
        
        # Value range verification
        if analysis['collected_values']:
            min_collected = min(analysis['collected_values'])
            max_collected = max(analysis['collected_values'])
            print(f"\n  Collected value range: {min_collected} - {max_collected}")
            
            # Check for high-value collections (should reach up to 2000× when such symbols appear)
            high_values = [v for v in analysis['collected_values'] if v >= 1000]
            if high_values:
                print(f"  High-value collections (>=1000): {len(high_values)} events, max: {max(high_values)}")
            
            very_high_values = [v for v in analysis['collected_values'] if v >= 2000]
            if very_high_values:
                print(f"  Very high collections (>=2000): {len(very_high_values)} events, max: {max(very_high_values)}")
    
    # NEW DETAILED DISTRIBUTIONS
    print(f"\nCW PER BONUS DISTRIBUTION:")
    cw_0 = sum(1 for x in analysis['cw_per_bonus'] if x == 0)
    cw_1_3 = sum(1 for x in analysis['cw_per_bonus'] if 1 <= x <= 3)
    cw_4_7 = sum(1 for x in analysis['cw_per_bonus'] if 4 <= x <= 7)
    cw_8_plus = sum(1 for x in analysis['cw_per_bonus'] if x >= 8)
    total_bonuses = len(analysis['cw_per_bonus'])
    
    print(f"  0 CWs: {cw_0} bonuses ({cw_0/total_bonuses*100:.1f}%)")
    print(f"  1-3 CWs: {cw_1_3} bonuses ({cw_1_3/total_bonuses*100:.1f}%)")
    print(f"  4-7 CWs: {cw_4_7} bonuses ({cw_4_7/total_bonuses*100:.1f}%)")
    print(f"  8+ CWs: {cw_8_plus} bonuses ({cw_8_plus/total_bonuses*100:.1f}%)")
    
    print(f"\nCC PER SPIN DISTRIBUTION:")
    total_spins = sum(analysis['cc_per_spin_distribution'].values())
    for cc_count in sorted(analysis['cc_per_spin_distribution'].keys()):
        frequency = analysis['cc_per_spin_distribution'][cc_count]
        print(f"  {cc_count} CCs: {frequency} spins ({frequency/total_spins*100:.1f}%)")
    
    print(f"\nCC PER BONUS DISTRIBUTION:")
    if analysis['cc_per_bonus']:
        avg_cc_per_bonus = sum(analysis['cc_per_bonus']) / len(analysis['cc_per_bonus'])
        max_cc = max(analysis['cc_per_bonus'])
        print(f"  Average CC per bonus: {avg_cc_per_bonus:.1f}")
        print(f"  Max CC in a bonus: {max_cc}")
        
        # Small vs big chocolates (assuming >5 CC is "big")
        small_cc_bonuses = sum(1 for x in analysis['cc_per_bonus'] if 1 <= x <= 5)
        big_cc_bonuses = sum(1 for x in analysis['cc_per_bonus'] if x > 5)
        print(f"  Small CC bonuses (1-5): {small_cc_bonuses} ({small_cc_bonuses/total_bonuses*100:.1f}%)")
        print(f"  Big CC bonuses (6+): {big_cc_bonuses} ({big_cc_bonuses/total_bonuses*100:.1f}%)")
    
    print(f"\nLEVEL PROGRESSION STATS:")
    if analysis['levels_reached']:
        level_counts = Counter(analysis['levels_reached'])
        avg_level = sum(analysis['levels_reached']) / len(analysis['levels_reached'])
        print(f"  Average level per bonus: {avg_level:.2f}")
        
        for level in sorted(level_counts.keys()):
            count = level_counts[level]
            print(f"  Reach Level {level}: {count} bonuses ({count/total_bonuses*100:.1f}%)")
        
        # Verify level progression from CW counts
        print(f"\nLEVEL PROGRESSION VERIFICATION (from CW counts):")
        level_4_plus = sum(1 for cw_count in analysis['cw_per_bonus'] if cw_count >= 4)
        level_8_plus = sum(1 for cw_count in analysis['cw_per_bonus'] if cw_count >= 8)
        level_12_plus = sum(1 for cw_count in analysis['cw_per_bonus'] if cw_count >= 12)
        
        print(f"  Bonuses with >=4 CWs (Level 2+): {level_4_plus} ({level_4_plus/total_bonuses*100:.1f}%)")
        print(f"  Bonuses with >=8 CWs (Level 3+): {level_8_plus} ({level_8_plus/total_bonuses*100:.1f}%)")
        print(f"  Bonuses with >=12 CWs (Level 4): {level_12_plus} ({level_12_plus/total_bonuses*100:.1f}%)")
    
    print(f"\nCOLLECTIONS PER BONUS DISTRIBUTION:")
    if analysis['collections_per_bonus']:
        collection_counts = Counter(analysis['collections_per_bonus'])
        avg_collections = sum(analysis['collections_per_bonus']) / len(analysis['collections_per_bonus'])
        print(f"  Average collections per bonus: {avg_collections:.2f}")
        
        for collections in sorted(collection_counts.keys()):
            count = collection_counts[collections]
            print(f"  {collections} collections: {count} bonuses ({count/total_bonuses*100:.1f}%)")
    
    print(f"\nCOLLECTED VALUE ANALYSIS:")
    if analysis['collected_values']:
        avg_value = sum(analysis['collected_values']) / len(analysis['collected_values'])
        max_value = max(analysis['collected_values'])
        min_value = min(analysis['collected_values'])
        print(f"  Average collected value per event: {avg_value:.2f}")
        print(f"  Value range: {min_value} - {max_value}")
        
        # Value distribution
        small_values = sum(1 for x in analysis['collected_values'] if x <= 2)
        medium_values = sum(1 for x in analysis['collected_values'] if 3 <= x <= 6)
        big_values = sum(1 for x in analysis['collected_values'] if x > 6)
        total_collections = len(analysis['collected_values'])
        
        print(f"  Small values (1-2): {small_values} ({small_values/total_collections*100:.1f}%)")
        print(f"  Medium values (3-6): {medium_values} ({medium_values/total_collections*100:.1f}%)")
        print(f"  Big values (7+): {big_values} ({big_values/total_collections*100:.1f}%)")
    
    print(f"\nDEAD SPIN STREAK ANALYSIS:")
    if analysis['dead_spin_streaks']:
        avg_streak = sum(analysis['dead_spin_streaks']) / len(analysis['dead_spin_streaks'])
        max_streak = max(analysis['dead_spin_streaks'])
        print(f"  Average dead spin streak: {avg_streak:.1f} spins")
        print(f"  Longest dead streak: {max_streak} spins")
        
        short_streaks = sum(1 for x in analysis['dead_spin_streaks'] if x <= 3)
        medium_streaks = sum(1 for x in analysis['dead_spin_streaks'] if 4 <= x <= 7)
        long_streaks = sum(1 for x in analysis['dead_spin_streaks'] if x > 7)
        total_streaks = len(analysis['dead_spin_streaks'])
        
        print(f"  Short streaks (1-3): {short_streaks} ({short_streaks/total_streaks*100:.1f}%)")
        print(f"  Medium streaks (4-7): {medium_streaks} ({medium_streaks/total_streaks*100:.1f}%)")
        print(f"  Long streaks (8+): {long_streaks} ({long_streaks/total_streaks*100:.1f}%)")
        
    # (after your existing print blocks)
    print(f"\nHEADLINE RATES:")
    print(f"  Spins with >=1 CW: {analysis['spins_with_cw'] / analysis['total_bonus_spins'] * 100:.1f}%")
    print(f"  Spins with >=1 CC: {analysis['spins_with_cc'] / analysis['total_bonus_spins'] * 100:.1f}%")

if __name__ == "__main__":
    main()