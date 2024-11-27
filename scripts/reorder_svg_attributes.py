import xml.etree.ElementTree as ET
import sys
import os
import re
import stat

def is_merge_conflict_file(content):
    return re.search(r'<<<<<<< HEAD|=======|>>>>>>> ', content)

def make_writable(file_path):
    """Ensure the file is writable"""
    try:
        # Get current file permissions
        current_permissions = os.stat(file_path).st_mode
        # Add write permissions for the owner
        os.chmod(file_path, current_permissions | stat.S_IWRITE)
    except Exception as e:
        print(f"Could not modify file permissions for {file_path}: {e}")

def reorder_svg_attributes(input_file, output_file=None):
    try:
        # Ensure file is writable
        make_writable(input_file)

        # Read the file content first to check for merge conflicts
        with open(input_file, 'r') as f:
            content = f.read()

        # Skip merge conflict files
        if is_merge_conflict_file(content):
            print(f"Skipping merge conflict file: {input_file}")
            return None

        # Parse the SVG file
        root = ET.fromstring(content)

        # Specific order of attributes for the SVG tag
        attribute_order = [
            'xmlns',     # Namespace always first
            'width',     # Dimensional attributes
            'height',    
            'viewBox',   
            'fill',      # Style-related attributes
            'stroke',
            'stroke-width',
            'stroke-linecap',
            'stroke-linejoin'
        ]

        # Create a new ordered attribute dictionary
        ordered_attrib = {}

        # Add attributes in the specified order
        for attr in attribute_order:
            if attr in root.attrib:
                ordered_attrib[attr] = root.attrib[attr]

        # Add any remaining attributes that weren't in our predefined order
        for attr, value in root.attrib.items():
            if attr not in ordered_attrib:
                ordered_attrib[attr] = value

        # Recreate the element with ordered attributes
        root.attrib.clear()
        root.attrib.update(ordered_attrib)

        # Convert back to string
        compressed_svg = ET.tostring(root, encoding='unicode', method='xml')
        
        # Remove any XML declaration if present
        compressed_svg = re.sub(r'<\?xml.*?\?>\s*', '', compressed_svg)

        # Write to file or return the result
        if output_file:
            with open(output_file, 'w') as f:

                # Remove namespace prefixes
                compressed_svg = compressed_svg.replace('<ns0:svg xmlns:ns0=', '<svg xmlns=')
                compressed_svg = compressed_svg.replace('ns0:', '')

                f.write(compressed_svg)
            print(f"Reordered: {input_file}")
        
        return compressed_svg

    except PermissionError:
        print(f"Permission denied when processing {input_file}. Check file permissions.")
        return None
    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        return None

def process_directory(input_dir):
    processed_files = 0
    skipped_files = 0
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.svg'):
            input_path = os.path.join(input_dir, filename)
            
            # Reorder in-place
            result = reorder_svg_attributes(input_path, input_path)
            
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
        reorder_svg_attributes(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python reorder_svg_attributes.py <input_directory>")
        print("   or: python reorder_svg_attributes.py <input_file> <output_file>")