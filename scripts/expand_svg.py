import xml.etree.ElementTree as ET
import sys
import os
import re

def is_merge_conflict_file(content):
    return re.search(r'<<<<<<< HEAD|=======|>>>>>>> ', content)

def prettify_svg(input_file, output_file):
    try:
        with open(input_file, 'r') as f:
            content = f.read()
        
        # Check for merge conflict markers
        if is_merge_conflict_file(content):
            print(f"Skipping merge conflict file: {input_file}")
            return False

        tree = ET.fromstring(content)
        
        # Preserve original attributes order and formatting
        attrib_str = ' '.join(f'{k}="{v}"' for k, v in tree.attrib.items())
        
        # Prepare child elements
        child_elements = '\n    '.join(
            ET.tostring(child, encoding='unicode').strip() 
            for child in tree
        )
        
        # Construct formatted SVG
        formatted_svg = f'<svg {attrib_str}>\n    {child_elements}\n</svg>'
        
        with open(output_file, 'w') as f:
            f.write(formatted_svg)
        return True
    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        return False

def process_directory(input_dir):
    processed_files = 0
    skipped_files = 0
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.svg'):
            input_path = os.path.join(input_dir, filename)
            output_path = input_path
            
            result = prettify_svg(input_path, output_path)
            
            if result:
                processed_files += 1
            else:
                skipped_files += 1
    
    print(f"Processed: {processed_files} files")
    print(f"Skipped: {skipped_files} files")

if __name__ == '__main__':
    if len(sys.argv) == 2 and os.path.isdir(sys.argv[1]):
        process_directory(sys.argv[1])
    elif len(sys.argv) == 3:
        prettify_svg(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python normalize_svg.py <input_directory>")
        print("   or: python normalize_svg.py <input_file> <output_file>")