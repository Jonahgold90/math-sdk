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

def extract_cc_values(board):
    """Extract actual CC values if available, otherwise return count-based proxy"""
    cc_values = []
    for row in board:
        for cell in row:
            if cell['name'] == 'CC':
                # Try to get actual value, fallback to proxy
                if 'value' in cell:
                    cc_values.append(cell['value'])
                elif 'payout' in cell:
                    cc_values.append(cell['payout'])
                else:
                    cc_values.append(1)  # Proxy value
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
        
        for event in book['events']:
            if event.get('type') != 'reveal':
                continue
                
            spin_count += 1
            analysis['total_bonus_spins'] += 1
            
            board = event.get('board', [])
            symbols = extract_board_symbols(board)
            cc_values = extract_cc_values(board)
            
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
                if cw_count_this_bonus >= 12:
                    level_this_bonus = 4
                elif cw_count_this_bonus >= 8:
                    level_this_bonus = 3
                elif cw_count_this_bonus >= 4:
                    level_this_bonus = 2

            
            if cw_on_board > 0 and cc_on_board > 0:
                analysis['cw_cc_co_occurrence'] += 1
                collections_this_bonus += 1
                
                # Record dead streak before resetting
                if dead_spin_streak > 0:
                    analysis['dead_spin_streaks'].append(dead_spin_streak)
                dead_spin_streak = 0  # Reset dead streak
                
                # Calculate collected value using actual CC values if available
                if cc_values and any(v != 1 for v in cc_values):
                    # Use actual CC values
                    collected_value = cw_on_board * sum(cc_values) * level_this_bonus
                else:
                    # Use proxy: CW count * CC count * level
                    collected_value = cw_on_board * cc_on_board * level_this_bonus
                analysis['collected_values'].append(collected_value)
                
                # Determine if using real values or proxy
                using_real_values = cc_values and any(v != 1 for v in cc_values)
                
                analysis['collection_events'].append({
                    'bonus_id': book['id'],
                    'spin': spin_count,
                    'cw_count': cw_on_board,
                    'cc_count': cc_on_board,
                    'level': level_this_bonus,
                    'collected_value': collected_value,
                    'cc_values': cc_values if using_real_values else None,
                    'value_type': 'real' if using_real_values else 'proxy',
                })
                    
            elif cw_on_board > 0 and cc_on_board == 0:
                analysis['dead_cws'] += cw_on_board
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
    print(f"  Dead CWs (no CC): {analysis['dead_cws']}")
    
    print(f"\nCHOCOLATE CASH ANALYSIS:")
    print(f"  Total CC Events: {total_ccs:,}")
    print(f"  Orphan Chocolates (no CW): {analysis['orphan_chocolates']}")
    
    print(f"\nCOLLECTION MECHANICS:")
    print(f"  Total Collection Events: {len(analysis['collection_events'])}")
    print(f"  CW-CC Co-occurrence: {analysis['cw_cc_co_occurrence']} events")
    
    if analysis['collection_events']:
        print(f"\nSAMPLE COLLECTION EVENTS:")
        real_values = sum(1 for event in analysis['collection_events'] if event.get('value_type') == 'real')
        proxy_values = len(analysis['collection_events']) - real_values
        print(f"  Value Types: {real_values:,} real, {proxy_values:,} proxy")
        
        for i, event in enumerate(analysis['collection_events'][:5]):
            value_type = event.get('value_type', 'proxy')
            print(f"  Event {i+1}: {event['cw_count']} CW + {event['cc_count']} CC at Level {event['level']} = {event['collected_value']} value ({value_type}) (Bonus {event['bonus_id']}, Spin {event['spin']})")
    
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
    print(f"  Spins with ≥1 CW: {analysis['spins_with_cw'] / analysis['total_bonus_spins'] * 100:.1f}%")
    print(f"  Spins with ≥1 CC: {analysis['spins_with_cc'] / analysis['total_bonus_spins'] * 100:.1f}%")

if __name__ == "__main__":
    main()