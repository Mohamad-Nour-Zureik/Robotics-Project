import re

# ============= CONFIGURATION =============
# Edit this array to change the base colors (8 colors for 8 bases)
ARRAY = ['y', 'r', 'b', 'g',
         'r', 'g', 'b', 'y']
# =========================================

# Color name to RGB mapping
COLOR_MAP = {
    'r': '1 0 0',
    'g': '0 1 0',
    'b': '0 0 1',
    'y': '1 1 0',
}

def find_matching_brace(content, start_pos):
    """Find the position of the matching closing brace."""
    depth = 0
    i = start_pos
    while i < len(content):
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1

def update_world_file(input_file, output_file, color_array):
    """
    Updates the Webots world file with new base colors.
    
    Args:
        input_file: Path to the input .wbt file
        output_file: Path to the output .wbt file
        color_array: List of color names to apply to the bases
    """
    
    # Validate colors
    for color in color_array:
        if color not in COLOR_MAP:
            print(f"Warning: Color '{color}' not found in COLOR_MAP. Available colors: {list(COLOR_MAP.keys())}")
            return False
    
    # Read the file
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Find the start of the Pose block we want to replace
    search_str = 'Pose {\n  translation -1.653 0.35 0.0001'
    start_pos = content.find(search_str)
    
    if start_pos == -1:
        print("Error: Could not find the base color section in the world file.")
        print("Looking for Pose with translation -1.653 0.35 0.0001")
        return False
    
    # Find the opening brace of this Pose block
    brace_pos = content.find('{', start_pos)
    
    # Find the matching closing brace
    end_pos = find_matching_brace(content, brace_pos)
    
    if end_pos == -1:
        print("Error: Could not find matching closing brace.")
        return False
    
    # Generate new Pose children for the 8 bases
    base_positions = [
        '0 0 0.0001',
        '0.12 0 0.0001',
        '0.24 0 0.0001',
        '0.36 0 0.0001',
        '0.48 0 0.0001',
        '0.6 0 0.0001',
        '0.72 0 0.0001',
        '0.84 0 0.0001'
    ]
    
    new_poses = []
    for i, color in enumerate(color_array[:8]):  # Limit to 8 bases
        rgb = COLOR_MAP[color]
        pose_text = f"""        Pose {{
          translation {base_positions[i]}
          children [
            Shape {{
              appearance PBRAppearance {{
                baseColor {rgb}
                roughness 1
                metalness 0
              }}
              geometry Plane {{
                size 0.12 0.5
              }}
            }}
          ]
        }}"""
        new_poses.append(pose_text)
    
    new_children = '\n'.join(new_poses)
    
    # Build the complete replacement block - note the proper closing brackets
    replacement = f"""Pose {{
  translation -1.653 0.35 0.0001
  children [
    Group {{
      children [
{new_children}
      ]
    }}
  ]
}}"""
    
    # Replace the entire matched block
    new_content = content[:start_pos] + replacement + content[end_pos+1:]
    
    # Write the updated content
    with open(output_file, 'w') as f:
        f.write(new_content)
    
    print(f"Successfully updated world file!")
    print(f"Base colors set to: {color_array}")
    return True


if __name__ == "__main__":
    import os
    import glob
    
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"Looking for .wbt files in: {os.getcwd()}")
    print(f"Files in directory: {os.listdir('.')}")
    
    # Automatically find .wbt file in current directory
    wbt_files = glob.glob("*.wbt")
    
    if not wbt_files:
        print("\nError: No .wbt file found in the current directory.")
        print(f"Current directory: {os.getcwd()}")
        exit(1)
    elif len(wbt_files) > 1:
        print("Multiple .wbt files found. Please specify which one to use:")
        for i, file in enumerate(wbt_files):
            print(f"  {i+1}. {file}")
        choice = int(input("Enter number: ")) - 1
        input_file = wbt_files[choice]
    else:
        input_file = wbt_files[0]
    
    output_file = input_file  # Overwrites the original file
    
    print(f"Using world file: {input_file}")
    
    # Update the world file with colors from ARRAY
    success = update_world_file(input_file, output_file, ARRAY)
    
    if success:
        print("\n✓ World file updated successfully!")
        for i in range(8):
            if i < len(ARRAY):
                print(f"  Base {i+1}: {ARRAY[i]}")
            else:
                print(f"  Base {i+1}: N/A")
    else:
        print("\n✗ Failed to update world file.")