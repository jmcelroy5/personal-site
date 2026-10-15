#!/usr/bin/env python3
"""
CSV to YAML Converter

A CLI script that converts CSV files to YAML format with configurable columns.

Usage:
    python3 csv_to_yaml.py input.csv -c "column1,column2,column3" [options]

Example:
    python3 csv_to_yaml.py books.csv -c "Title,Author,Year Published,Date Read"
"""

import argparse
import csv
import sys
import json
from pathlib import Path


def format_yaml_value(value):
    """
    Format a value for YAML output.
    """
    if value == '':
        return ''
    elif value.isdigit():
        return int(value)
    elif value.replace('.', '', 1).isdigit():
        return float(value)
    elif value.lower() in ['true', 'false']:
        return value.lower() == 'true'
    else:
        # Escape special characters and quote strings that need it
        if any(char in value for char in ['"', "'", ':', '[', ']', '{', '}', '#', '|', '>', '&', '*', '!', '%', '@', '`']):
            return f'"{value}"'
        return value


def dict_to_yaml(data, indent=0):
    """
    Convert a dictionary to YAML format string.
    """
    lines = []
    indent_str = '  ' * indent
    
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                lines.append(f"{indent_str}-")
                lines.append(dict_to_yaml(item, indent + 1))
            else:
                lines.append(f"{indent_str}- {format_yaml_value(item)}")
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{indent_str}{key}:")
                lines.append(dict_to_yaml(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{indent_str}{key}:")
                lines.append(dict_to_yaml(value, indent + 1))
            else:
                lines.append(f"{indent_str}{key}: {format_yaml_value(value)}")
    
    return '\n'.join(lines)


def csv_to_yaml(input_file, columns, output_file=None, delimiter=',', quotechar='"', append_mode=False):
    """
    Convert CSV file to YAML format.
    
    Args:
        input_file (str): Path to input CSV file
        columns (list): List of column names to include
        output_file (str, optional): Path to output file. If None, prints to stdout
        delimiter (str): CSV delimiter character
        quotechar (str): CSV quote character
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            # Read CSV and get fieldnames
            csv_reader = csv.DictReader(file, delimiter=delimiter, quotechar=quotechar)
            fieldnames = csv_reader.fieldnames
            
            # Validate requested columns exist
            missing_columns = [col for col in columns if col not in fieldnames]
            if missing_columns:
                print(f"Error: The following columns were not found in the CSV: {', '.join(missing_columns)}", file=sys.stderr)
                print(f"Available columns: {', '.join(fieldnames)}", file=sys.stderr)
                sys.exit(1)
            
            # Create list of dictionaries for YAML
            yaml_data = []
            
            for row in csv_reader:
                # Create dictionary with only requested columns
                yaml_row = {}
                for col in columns:
                    value = row[col].strip() if row[col] else ''
                    
                    # Convert date format from YYYY/MM/DD to YYYY-MM-DD
                    if col == 'Date Read' and value:
                        value = value.replace('/', '-')
                    
                    # Convert field names to snake_case
                    snake_case_key = col.lower().replace(' ', '_').replace('-', '_')
                    yaml_row[snake_case_key] = value
                yaml_data.append(yaml_row)
            
            # Convert to YAML
            result = dict_to_yaml(yaml_data)
            
            if output_file:
                mode = 'a' if append_mode else 'w'
                with open(output_file, mode, encoding='utf-8') as out_file:
                    out_file.write(result)
                action = "appended to" if append_mode else "written to"
                print(f"YAML data {action} {output_file}")
            else:
                print(result)
                
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Convert CSV file to YAML format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert with specific columns
  python csv_to_yaml.py books.csv -c "Title,Author,Year Published"
  
  # Save to file
  python csv_to_yaml.py books.csv -c "Title,Author" -o books.yml
  
  # Use different delimiter
  python csv_to_yaml.py data.tsv -c "col1,col2" --delimiter "\\t"
        """
    )
    
    parser.add_argument('input_file', help='Input CSV file path')
    parser.add_argument('-c', '--columns', required=True, 
                       help='Comma-separated list of column names to include')
    parser.add_argument('-o', '--output', 
                       help='Output file path (default: print to stdout)')
    parser.add_argument('--delimiter', default=',', 
                       help='CSV delimiter character (default: comma)')
    parser.add_argument('--quotechar', default='"', 
                       help='CSV quote character (default: double quote)')
    parser.add_argument('--append', action='store_true',
                       help='Append to output file instead of overwriting')
    
    args = parser.parse_args()
    
    # Parse columns
    columns = [col.strip() for col in args.columns.split(',')]
    
    # Handle tab delimiter
    delimiter = '\t' if args.delimiter == '\\t' else args.delimiter
    
    csv_to_yaml(
        input_file=args.input_file,
        columns=columns,
        output_file=args.output,
        delimiter=delimiter,
        quotechar=args.quotechar,
        append_mode=args.append
    )


if __name__ == '__main__':
    main()
