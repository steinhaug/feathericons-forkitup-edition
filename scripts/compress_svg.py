import xml.etree.ElementTree as ET
import sys
import os
import re

def is_merge_conflict_file(content):
    return re.search(r'<<<<<<< HEAD|=======|>>>>>>> ', content)

def compress_svg(input_file, output_file=None):
    try:
        # Parse the SVG file
        tree = ET.parse(input_file)
        root = tree.getroot()

        # Remove unnecessary whitespace from attributes
        for elem in root.iter():
            # Clean up attribute values
            elem.attrib = {k: re.sub(r'\s+', ' ', v.strip()) for k, v in elem.attrib.items()}

        # Convert to a compact single-line string
        compressed_svg = ET.tostring(root, encoding='unicode', method='xml')
        
        # Remove extra whitespace between tags
        compressed_svg = re.sub(r'>\s+<', '><', compressed_svg)
        
        # Optional: remove comments
        compressed_svg = re.sub(r'<!--.*?-->', '', compressed_svg)

        # Write to file or return the compressed SVG
        if output_file:
            with open(output_file, 'w') as f:
                f.write(compressed_svg)
            print(f"Compressed: {input_file}")
        
        return compressed_svg

    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        return None

def process_directory(input_dir):
    processed_files = 0
    skipped_files = 0
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.svg'):
            input_path = os.path.join(input_dir, filename)
            
            # Compress in-place
            result = compress_svg(input_path, input_path)
            
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
        compress_svg(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python compress_svg.py <input_directory>")
        print("   or: python compress_svg.py <input_file> <output_file>")