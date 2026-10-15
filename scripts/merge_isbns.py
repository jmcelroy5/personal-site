#!/usr/bin/env python3
"""
ISBN Merge Script

Merges corrected ISBNs from an old books.yml file into a new books.yml file.
Matches books by title and updates ISBNs where they differ.

Usage:
    python3 scripts/merge_isbns.py old_books.yml new_books.yml output.yml
"""

import argparse
import sys
import re
from pathlib import Path


def parse_yaml_file(file_path):
    """
    Parse a YAML file and return the list of books.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            books = []
            current_book = {}
            
            for line in file:
                line = line.rstrip('\n')
                
                # Skip empty lines and front matter
                if not line.strip() or line.startswith('---'):
                    continue
                
                # Start of new book entry
                if line.strip() == '-':
                    if current_book:
                        books.append(current_book)
                    current_book = {}
                # Parse key-value pairs
                elif line.startswith('  ') and ':' in line:
                    # Remove leading spaces and split on first colon
                    clean_line = line.strip()
                    colon_pos = clean_line.find(':')
                    if colon_pos > 0:
                        key = clean_line[:colon_pos].strip()
                        value = clean_line[colon_pos + 1:].strip()
                        
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        
                        current_book[key] = value
            
            # Don't forget the last book
            if current_book:
                books.append(current_book)
            
            return books
            
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)


def create_lookup(old_books):
    """
    Create a lookup dictionary from title to book data (ISBN and book_id).
    """
    lookup = {}
    for book in old_books:
        title = book.get('title', '').strip()
        isbn = book.get('isbn', '').strip()
        book_id = book.get('book_id', '').strip()
        if title:
            lookup[title.lower()] = {
                'isbn': isbn,
                'book_id': book_id
            }
    return lookup


def merge_data(new_books, lookup):
    """
    Update ISBNs and book_ids in new_books based on the lookup table.
    """
    updated_count = 0
    not_found_count = 0
    
    for book in new_books:
        title = book.get('title', '').strip()
        current_isbn = book.get('isbn', '').strip()
        current_book_id = book.get('goodreads_id', '').strip()
        
        if title:
            title_key = title.lower()
            if title_key in lookup:
                lookup_data = lookup[title_key]
                corrected_isbn = lookup_data.get('isbn', '')
                corrected_book_id = lookup_data.get('book_id', '')
                
                updated = False
                if current_isbn != corrected_isbn and corrected_isbn:
                    book['isbn'] = corrected_isbn
                    updated = True
                if current_book_id != corrected_book_id and corrected_book_id:
                    book['book_id'] = corrected_book_id
                    updated = True
                
                if updated:
                    updated_count += 1
                    print(f"Updated: '{title}' - ISBN: {current_isbn} → {corrected_isbn}, ID: {current_book_id} → {corrected_book_id}")
            else:
                not_found_count += 1
                print(f"Not found in lookup: '{title}'")
    
    return updated_count, not_found_count


def write_yaml_file(books, output_path):
    """
    Write books to YAML file in the same format as the original.
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            for i, book in enumerate(books):
                if i > 0:
                    file.write('\n')
                file.write('-\n')
                for key, value in book.items():
                    if isinstance(value, str) and ('"' in value or ':' in value or value.startswith('#')):
                        file.write(f'  {key}: "{value}"\n')
                    else:
                        file.write(f'  {key}: {value}\n')
        
        print(f"Updated books written to {output_path}")
        
    except Exception as e:
        print(f"Error writing file '{output_path}': {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Merge corrected ISBNs from old books.yml into new books.yml',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Merge ISBNs from old file into new file
  python3 scripts/merge_isbns.py books_copy.yml books.yml books_merged.yml
  
  # Update in place (backup recommended)
  python3 scripts/merge_isbns.py books_copy.yml books.yml books.yml
        """
    )
    
    parser.add_argument('old_file', help='Path to old books.yml with corrected ISBNs')
    parser.add_argument('new_file', help='Path to new books.yml')
    parser.add_argument('output_file', help='Path for output file')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be updated without writing file')
    
    args = parser.parse_args()
    
    print("Reading old books file...")
    old_books = parse_yaml_file(args.old_file)
    print(f"Found {len(old_books)} books in old file")
    
    print("Reading new books file...")
    new_books = parse_yaml_file(args.new_file)
    print(f"Found {len(new_books)} books in new file")
    
    print("Creating lookup table...")
    lookup = create_lookup(old_books)
    print(f"Created lookup for {len(lookup)} books")
    
    print("\nMerging ISBNs and book_ids...")
    updated_count, not_found_count = merge_data(new_books, lookup)
    
    print(f"\nSummary:")
    print(f"  Books updated: {updated_count}")
    print(f"  Books not found in lookup: {not_found_count}")
    print(f"  Total books processed: {len(new_books)}")
    
    if not args.dry_run:
        print(f"\nWriting merged books to {args.output_file}...")
        write_yaml_file(new_books, args.output_file)
    else:
        print("\nDry run completed - no file written")


if __name__ == '__main__':
    main()
