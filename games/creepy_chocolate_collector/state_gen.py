"""
Simplified, 100% accurate Big Bass collection analyzer
No fallbacks, no mock data, only real collection events
"""

import json
import zstandard as zstd
import os
from collections import defaultdict, Counter

def load_books(file_path):
    """Load compressed game books"""
    with open(file_path, 'rb') as f:
        dctx = zstd.ZstdDecompressor()
        with dctx.stream_reader(f) as reader:
            decompressed = reader.read()
            lines = decompressed.decode('utf-8').strip().split('\n')
            return [json.loads(line) for line in lines if line.strip()]

def analyze_collections(books):
    """Analyze only actual collection events - no guessing"""
    
    # Raw counters
    total_bonuses = len(books)
    total_spins = 0
    total_cw_symbols = 0
    total_cc_symbols = 0
    
    # Collection data - only from real collection events
    collection_events = []
    collections_per_bonus = []
    
    # Board analysis
    cw_per_bonus = []
    cc_per_bonus = []
    
    for book in books:
        if not book.get('events'):
            continue
            
        # Count spins and symbols for this bonus
        bonus_spins = 0
        bonus_cws = 0
        bonus_ccs = 0
        bonus_collections = 0
        
        # Process all events for this bonus
        for event in book['events']:
            event_type = event.get('type')
            
            if event_type == 'reveal':
                bonus_spins += 1
                total_spins += 1
                
                # Count symbols on this spin
                board = event.get('board', [])
                spin_cws = 0
                spin_ccs = 0
                
                for row in board:
                    for cell in row:
                        if cell.get('name') == 'CW':
                            spin_cws += 1
                            total_cw_symbols += 1
                            bonus_cws += 1
                        elif cell.get('name') == 'CC':
                            spin_ccs += 1  
                            total_cc_symbols += 1
                            bonus_ccs += 1
            
            elif event_type == 'collection':
                # Real collection event - use exactly as logged
                bonus_collections += 1
                collection_events.append({
                    'book_id': book.get('id'),
                    'cw_count': event.get('cw_count', 0),
                    'cc_count': event.get('cc_count', 0),
                    'cc_total_value': event.get('cc_total_value', 0),
                    'level': event.get('level', 1),
                    'collected_amount': event.get('collected_amount', 0)
                })
        
        # Store per-bonus stats
        collections_per_bonus.append(bonus_collections)
        cw_per_bonus.append(bonus_cws)
        cc_per_bonus.append(bonus_ccs)
    
    return {
        'total_bonuses': total_bonuses,
        'total_spins': total_spins,
        'total_cw_symbols': total_cw_symbols,
        'total_cc_symbols': total_cc_symbols,
        'collection_events': collection_events,
        'collections_per_bonus': collections_per_bonus,
        'cw_per_bonus': cw_per_bonus,
        'cc_per_bonus': cc_per_bonus
    }

def print_analysis(data):
    """Print analysis results"""
    
    print(f"ACCURATE BIG BASS ANALYSIS")
    print(f"=" * 50)
    
    print(f"\nBASIC STATS:")
    print(f"  Total Bonuses: {data['total_bonuses']:,}")
    print(f"  Total Spins: {data['total_spins']:,}")
    print(f"  Avg Spins per Bonus: {data['total_spins']/data['total_bonuses']:.1f}")
    
    print(f"\nSYMBOL COUNTS:")
    print(f"  Total CW Symbols: {data['total_cw_symbols']:,}")
    print(f"  Total CC Symbols: {data['total_cc_symbols']:,}")
    print(f"  CW Rate: {data['total_cw_symbols']/data['total_spins']*100:.1f}% of spins")
    print(f"  CC Rate: {data['total_cc_symbols']/data['total_spins']*100:.1f}% of spins")
    
    # Collection events analysis
    collections = data['collection_events']
    print(f"\nCOLLECTION EVENTS (REAL ONLY):")
    print(f"  Total Collection Events: {len(collections):,}")
    
    if collections:
        collected_amounts = [c['collected_amount'] for c in collections]
        cc_values = [c['cc_total_value'] for c in collections]
        levels = [c['level'] for c in collections]
        
        print(f"  Collected Amount Range: {min(collected_amounts)} - {max(collected_amounts)}")
        print(f"  Average Collected: {sum(collected_amounts)/len(collected_amounts):.1f}")
        print(f"  CC Value Range: {min(cc_values)} - {max(cc_values)}")
        print(f"  Level Range: {min(levels)} - {max(levels)}")
        
        # Show sample events
        print(f"\n  Sample Events:")
        for i, event in enumerate(collections[:5]):
            print(f"    {i+1}. Book {event['book_id']}: {event['cw_count']}CW + {event['cc_count']}CC × Level {event['level']} = {event['collected_amount']} (CC total: {event['cc_total_value']})")
    
    # Collections per bonus
    collections_per_bonus = data['collections_per_bonus']
    print(f"\nCOLLECTIONS PER BONUS:")
    print(f"  Average: {sum(collections_per_bonus)/len(collections_per_bonus):.2f}")
    
    collection_counts = Counter(collections_per_bonus)
    for collections in sorted(collection_counts.keys())[:15]:  # Show first 15
        count = collection_counts[collections]
        pct = count/len(collections_per_bonus)*100
        print(f"  {collections} collections: {count:,} bonuses ({pct:.1f}%)")
    
    # Zero collection analysis
    zero_collections = collection_counts[0]
    print(f"\n  Zero Collections: {zero_collections:,} bonuses ({zero_collections/len(collections_per_bonus)*100:.1f}%)")
    
    # CW per bonus analysis  
    cw_per_bonus = data['cw_per_bonus']
    print(f"\nCW PER BONUS:")
    print(f"  Average: {sum(cw_per_bonus)/len(cw_per_bonus):.1f}")
    cw_counts = Counter(cw_per_bonus)
    zero_cw = cw_counts[0]
    print(f"  Zero CW: {zero_cw:,} bonuses ({zero_cw/len(cw_per_bonus)*100:.1f}%)")
    
    # CC per bonus analysis
    cc_per_bonus = data['cc_per_bonus'] 
    print(f"\nCC PER BONUS:")
    print(f"  Average: {sum(cc_per_bonus)/len(cc_per_bonus):.1f}")
    cc_counts = Counter(cc_per_bonus)
    zero_cc = cc_counts[0]
    print(f"  Zero CC: {zero_cc:,} bonuses ({zero_cc/len(cc_per_bonus)*100:.1f}%)")

def main():
    """Main analysis function"""
    books_path = os.path.join("library", "publish_files", "books_bonus.jsonl.zst")
    
    if not os.path.exists(books_path):
        print(f"Error: {books_path} not found")
        return
    
    print("Loading bonus books...")
    books = load_books(books_path)
    print(f"Loaded {len(books)} bonus rounds")
    
    print("\nAnalyzing collections...")
    data = analyze_collections(books)
    
    print_analysis(data)

if __name__ == "__main__":
    main()