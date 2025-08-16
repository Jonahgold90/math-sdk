"""
Debug collection mechanism - find out why CW+CC combinations don't collect
"""

import json
import zstandard as zstd
import os
from collections import defaultdict

def load_books(file_path):
    with open(file_path, 'rb') as f:
        dctx = zstd.ZstdDecompressor()
        with dctx.stream_reader(f) as reader:
            decompressed = reader.read()
            lines = decompressed.decode('utf-8').strip().split('\n')
            return [json.loads(line) for line in lines if line.strip()]

def debug_collections(books):
    """Debug why collections aren't happening"""
    
    collection_events_by_book = defaultdict(list)
    
    # First, find all collection events
    for book in books:
        book_id = book.get('id')
        for event in book.get('events', []):
            if event.get('type') == 'collection':
                collection_events_by_book[book_id].append(event)
    
    print(f"Found collection events in {len(collection_events_by_book)} books")
    
    # Now analyze bonuses
    total_bonuses = 0
    bonuses_with_cw_cc = 0
    bonuses_with_collections = 0
    cw_cc_spins_total = 0
    collection_events_total = 0
    
    no_collection_examples = []
    
    for book in books[:100]:  # Check first 100 for detailed analysis
        book_id = book.get('id')
        total_bonuses += 1
        
        # Count CW+CC spins in this bonus
        cw_cc_spins_this_bonus = 0
        has_cw = False
        has_cc = False
        
        for event in book.get('events', []):
            if event.get('type') == 'reveal':
                board = event.get('board', [])
                cw_count = 0
                cc_count = 0
                
                for row in board:
                    for cell in row:
                        if cell.get('name') == 'CW':
                            cw_count += 1
                            has_cw = True
                        elif cell.get('name') == 'CC':
                            cc_count += 1
                            has_cc = True
                
                if cw_count > 0 and cc_count > 0:
                    cw_cc_spins_this_bonus += 1
                    cw_cc_spins_total += 1
        
        # Check if this bonus had both CW and CC
        if has_cw and has_cc:
            bonuses_with_cw_cc += 1
        
        # Check if this bonus had collection events
        collections_this_bonus = len(collection_events_by_book[book_id])
        if collections_this_bonus > 0:
            bonuses_with_collections += 1
            collection_events_total += collections_this_bonus
        
        # Record examples where CW+CC spins didn't produce collections
        if cw_cc_spins_this_bonus > 0 and collections_this_bonus == 0:
            no_collection_examples.append({
                'book_id': book_id,
                'cw_cc_spins': cw_cc_spins_this_bonus,
                'collections': collections_this_bonus
            })
    
    print(f"\nBONUS ANALYSIS (first 100 books):")
    print(f"  Total bonuses: {total_bonuses}")
    print(f"  Bonuses with both CW and CC: {bonuses_with_cw_cc} ({bonuses_with_cw_cc/total_bonuses*100:.1f}%)")
    print(f"  Bonuses with collection events: {bonuses_with_collections} ({bonuses_with_collections/total_bonuses*100:.1f}%)")
    print(f"  Total CW+CC spins: {cw_cc_spins_total}")
    print(f"  Total collection events: {collection_events_total}")
    print(f"  Collection rate: {collection_events_total/cw_cc_spins_total*100:.1f}% of CW+CC spins")
    
    print(f"\nEXAMPLES OF CW+CC SPINS WITHOUT COLLECTIONS:")
    for i, example in enumerate(no_collection_examples[:5]):
        print(f"  Book {example['book_id']}: {example['cw_cc_spins']} CW+CC spins, {example['collections']} collections")
    
    # Let's examine one specific case in detail
    if no_collection_examples:
        book_id = no_collection_examples[0]['book_id']
        print(f"\nDETAILED ANALYSIS OF BOOK {book_id}:")
        
        for book in books:
            if book.get('id') == book_id:
                spin_num = 0
                for event in book.get('events', []):
                    if event.get('type') == 'reveal':
                        spin_num += 1
                        board = event.get('board', [])
                        cw_symbols = []
                        cc_symbols = []
                        
                        for row_idx, row in enumerate(board):
                            for col_idx, cell in enumerate(row):
                                if cell.get('name') == 'CW':
                                    cw_symbols.append((row_idx, col_idx, cell))
                                elif cell.get('name') == 'CC':
                                    cc_symbols.append((row_idx, col_idx, cell))
                        
                        if cw_symbols and cc_symbols:
                            print(f"  Spin {spin_num}: {len(cw_symbols)} CW + {len(cc_symbols)} CC")
                            print(f"    CW symbols: {[cell for _, _, cell in cw_symbols]}")
                            print(f"    CC symbols: {[cell for _, _, cell in cc_symbols]}")
                break

def main():
    books_path = os.path.join("library", "publish_files", "books_bonus.jsonl.zst")
    
    if not os.path.exists(books_path):
        print(f"Error: {books_path} not found")
        return
    
    books = load_books(books_path)
    print(f"Loaded {len(books)} bonus rounds")
    
    debug_collections(books)

if __name__ == "__main__":
    main()