"""
Simple Big Bass level progression analysis - reads actual events only
"""

import json
import zstandard as zstd
import os
from collections import Counter

def load_books(file_path):
    with open(file_path, 'rb') as f:
        dctx = zstd.ZstdDecompressor()
        with dctx.stream_reader(f) as reader:
            decompressed = reader.read()
            lines = decompressed.decode('utf-8').strip().split('\n')
            return [json.loads(line) for line in lines if line.strip()]

def analyze_big_bass_events(books):
    """Analyze Big Bass mechanics from actual game events"""
    
    stats = {
        'total_bonuses': 0,
        'level_distributions': {1: 0, 2: 0, 3: 0, 4: 0},
        'collection_events': [],
        'level_advance_events': [],
        'total_collected': 0,
        'collections_by_level': Counter(),
        'values_by_level': {1: [], 2: [], 3: [], 4: []},
    }
    
    for book in books:
        if not book.get('events'):
            continue
            
        stats['total_bonuses'] += 1
        
        # Print progress every 5k books
        if stats['total_bonuses'] % 5000 == 0:
            print(f"  Processed {stats['total_bonuses']:,} bonuses...")
        
        max_level_reached = 1
        
        # Process each event in the bonus
        for event in book['events']:
            event_type = event.get('type')
            
            if event_type == 'level_advance':
                new_level = event.get('new_level', 1)
                max_level_reached = max(max_level_reached, new_level)
                stats['level_advance_events'].append({
                    'bonus_id': book.get('id'),
                    'spin': event.get('spin'),
                    'new_level': new_level
                })
                
            elif event_type == 'collection':
                level = event.get('level', 1)
                collected_amount = event.get('collected_amount', 0)
                cw_count = event.get('cw_count', 0)
                cc_count = event.get('cc_count', 0)
                cc_sum = event.get('cc_sum', 0)
                
                stats['collection_events'].append({
                    'bonus_id': book.get('id'),
                    'spin': event.get('spin'),
                    'level': level,
                    'cw_count': cw_count,
                    'cc_count': cc_count,
                    'cc_sum': cc_sum,
                    'collected_amount': collected_amount
                })
                
                stats['total_collected'] += collected_amount
                stats['collections_by_level'][level] += 1
                stats['values_by_level'][level].append(collected_amount)
        
        # Record the maximum level reached in this bonus
        stats['level_distributions'][max_level_reached] += 1
    
    return stats

def main():
    books_path = os.path.join("library", "publish_files", "books_bonus.jsonl.zst")
    books = load_books(books_path)
    print(f"Loaded {len(books):,} bonus rounds")
    
    stats = analyze_big_bass_events(books)
    
    print(f"\nBIG-BASS LEVEL PROGRESSION SUMMARY:")
    print(f"  Total bonuses analyzed: {stats['total_bonuses']:,}")
    
    print(f"\nLEVEL DISTRIBUTION (% of bonuses reaching each level):")
    multipliers = [1, 2, 3, 10]
    for level in [1, 2, 3, 4]:
        count = stats['level_distributions'][level]
        percentage = count / stats['total_bonuses'] * 100 if stats['total_bonuses'] > 0 else 0
        multiplier = multipliers[level - 1]
        print(f"  Level {level} (x{multiplier}): {count:,} bonuses ({percentage:.1f}%)")
    
    print(f"\nLEVEL ADVANCE EVENTS:")
    if stats['level_advance_events']:
        advance_counts = Counter(event['new_level'] for event in stats['level_advance_events'])
        print(f"  Total level advances: {len(stats['level_advance_events']):,}")
        for level in sorted(advance_counts.keys()):
            count = advance_counts[level]
            print(f"  Advances to Level {level}: {count:,} events")
    else:
        print(f"  No level advance events found")
    
    print(f"\nCOLLECTION EVENTS:")
    if stats['collection_events']:
        print(f"  Total collection events: {len(stats['collection_events']):,}")
        print(f"  Total amount collected: {stats['total_collected']:,.0f}")
        
        print(f"\n  Collections by level:")
        total_collections = len(stats['collection_events'])
        for level in [1, 2, 3, 4]:
            count = stats['collections_by_level'][level]
            percentage = count / total_collections * 100 if total_collections > 0 else 0
            multiplier = multipliers[level - 1]
            print(f"    Level {level} (x{multiplier}): {count:,} events ({percentage:.1f}%)")
        
        print(f"\n  Average collection values by level:")
        for level in [1, 2, 3, 4]:
            values = stats['values_by_level'][level]
            if values:
                avg_value = sum(values) / len(values)
                min_value = min(values)
                max_value = max(values)
                print(f"    Level {level}: avg={avg_value:.1f}, range={min_value}-{max_value}")
            else:
                print(f"    Level {level}: no collections")
        
        print(f"\n  Sample collection events:")
        for i, event in enumerate(stats['collection_events'][:5]):
            print(f"    Event {i+1}: {event['cw_count']} CW + {event['cc_count']} CC at Level {event['level']} = {event['collected_amount']} (CC sum: {event['cc_sum']})")
    else:
        print(f"  No collection events found")

if __name__ == "__main__":
    main()