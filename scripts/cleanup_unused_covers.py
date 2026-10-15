#!/usr/bin/env python3
"""
Book Cover Cleanup Script

Moves book cover images that are not referenced in books.yml to an 'unused' directory.
This helps clean up the book-covers folder by removing images for books not in your current collection.

Usage:
    python3 scripts/cleanup_unused_covers.py [options]

Example:
    python3 scripts/cleanup_unused_covers.py --dry-run
    python3 scripts/cleanup_unused_covers.py --move-unused
"""

import argparse
import os
import shutil
import sys
from pathlib import Path


def parse_books_yml(file_path):
    """
    Parse books.yml and extract all isbn values.
    """
    isbns = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            current_book = {}
            
            for line in file:
                line = line.rstrip('\n')
                
                # Skip empty lines and front matter
                if not line.strip() or line.startswith('---'):
                    continue
                
                # Start of new book entry
                if line.strip() == '-':
                    if current_book and 'isbn' in current_book:
                        isbns.add(current_book['isbn'])
                    current_book = {}
                # Parse key-value pairs
                elif line.startswith('  ') and ':' in line:
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
            if current_book and 'isbn' in current_book:
                isbns.add(current_book['isbn'])
        
        return isbns
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)


def get_cover_images(cover_dir):
    """
    Get all image files in the book-covers directory.
    """
    images = []
    
    if not os.path.exists(cover_dir):
        print(f"Error: Cover directory '{cover_dir}' not found.", file=sys.stderr)
        sys.exit(1)
    
    for file in os.listdir(cover_dir):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            # Extract ISBN from filename (remove extension)
            isbn = os.path.splitext(file)[0]
            images.append((file, isbn))
    
    return images


def cleanup_unused_covers(books_yml_path, cover_dir, dry_run=True):
    """
    Move unused book cover images to an 'unused' subdirectory.
    """
    print("Reading books.yml...")
    used_isbns = parse_books_yml(books_yml_path)
    print(f"Found {len(used_isbns)} books with ISBNs")
    
    print(f"Scanning cover directory: {cover_dir}")
    cover_images = get_cover_images(cover_dir)
    print(f"Found {len(cover_images)} cover images")
    
    # Find unused images
    unused_images = []
    used_images = []
    
    for filename, isbn in cover_images:
        if isbn in used_isbns:
            used_images.append(filename)
        else:
            unused_images.append(filename)
    
    print(f"\nSummary:")
    print(f"  Used images: {len(used_images)}")
    print(f"  Unused images: {len(unused_images)}")
    
    if unused_images:
        print(f"\nUnused images:")
        for img in unused_images:
            print(f"  - {img}")
    
    if dry_run:
        print(f"\n[DRY RUN] Would move {len(unused_images)} unused images to unused/ directory")
        return
    
    # Create unused directory if it doesn't exist
    unused_dir = os.path.join(cover_dir, 'unused')
    if unused_images and not os.path.exists(unused_dir):
        os.makedirs(unused_dir)
        print(f"Created directory: {unused_dir}")
    
    # Move unused images
    moved_count = 0
    for filename in unused_images:
        src_path = os.path.join(cover_dir, filename)
        dst_path = os.path.join(unused_dir, filename)
        
        try:
            shutil.move(src_path, dst_path)
            print(f"Moved: {filename}")
            moved_count += 1
        except Exception as e:
            print(f"Error moving {filename}: {e}", file=sys.stderr)
    
    print(f"\nSuccessfully moved {moved_count} unused images to {unused_dir}/")


def main():
    parser = argparse.ArgumentParser(
        description='Clean up unused book cover images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # See what would be moved (dry run)
  python3 scripts/cleanup_unused_covers.py --dry-run
  
  # Actually move unused images
  python3 scripts/cleanup_unused_covers.py --move-unused
  
  # Use custom paths
  python3 scripts/cleanup_unused_covers.py --books-file _data/books.yml --cover-dir assets/images/book-covers --dry-run
        """
    )
    
    parser.add_argument('--books-file', default='_data/books.yml',
                       help='Path to books.yml file (default: _data/books.yml)')
    parser.add_argument('--cover-dir', default='assets/images/book-covers',
                       help='Path to book-covers directory (default: assets/images/book-covers)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be moved without actually moving files')
    parser.add_argument('--move-unused', action='store_true',
                       help='Actually move unused images to unused/ directory')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.dry_run and not args.move_unused:
        print("Error: You must specify either --dry-run or --move-unused", file=sys.stderr)
        sys.exit(1)
    
    if args.dry_run and args.move_unused:
        print("Error: Cannot specify both --dry-run and --move-unused", file=sys.stderr)
        sys.exit(1)
    
    # Run the cleanup
    cleanup_unused_covers(
        books_yml_path=args.books_file,
        cover_dir=args.cover_dir,
        dry_run=args.dry_run
    )


if __name__ == '__main__':
    main()
