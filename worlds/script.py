import tkinter as tk
from tkinter import messagebox
import os
import glob

# Color name to RGB mapping
COLOR_MAP = {
    'r': '1 0 0',
    'g': '0 1 0',
    'b': '0 0 1',
    'y': '1 1 0',
}

# Color display names and hex values for GUI
COLOR_DISPLAY = {
    'r': {'name': 'Red', 'hex': '#FF0000'},
    'g': {'name': 'Green', 'hex': '#00FF00'},
    'b': {'name': 'Blue', 'hex': '#0000FF'},
    'y': {'name': 'Yellow', 'hex': '#FFFF00'},
}

# Available colors cycle
COLORS = ['r', 'g', 'b', 'y']

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
    
    # Read the file
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Find the start of the Pose block we want to replace
    search_str = 'Pose {\n  translation -1.653 0.35 0.0001'
    start_pos = content.find(search_str)
    
    if start_pos == -1:
        print("Error: Could not find the base color section in the world file.")
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
    
    # Build the complete replacement block
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


class ColorEditorGUI:
    def __init__(self, wbt_file):
        self.wbt_file = wbt_file
        self.colors = ['r', 'g', 'b', 'y', 'r', 'g', 'b', 'y']  # Default colors
        self.buttons = []
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Base Color Editor")
        self.root.geometry("600x250")
        self.root.resizable(False, False)
        
        # Title label
        title = tk.Label(self.root, text="Click each square to cycle colors", 
                        font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # File label
        file_label = tk.Label(self.root, text=f"Editing: {os.path.basename(wbt_file)}", 
                             font=("Arial", 10))
        file_label.pack(pady=5)
        
        # Frame for color squares
        colors_frame = tk.Frame(self.root)
        colors_frame.pack(pady=10)
        
        # Create 8 color buttons
        for i in range(8):
            btn_frame = tk.Frame(colors_frame)
            btn_frame.grid(row=0, column=i, padx=5)
            
            # Color square button
            btn = tk.Button(btn_frame, width=8, height=4, 
                           bg=COLOR_DISPLAY[self.colors[i]]['hex'],
                           relief=tk.RAISED, bd=3,
                           command=lambda idx=i: self.cycle_color(idx))
            btn.pack()
            self.buttons.append(btn)
            
            # Label below button
            label = tk.Label(btn_frame, text=f"Base {i+1}", font=("Arial", 9))
            label.pack()
        
        # Save button
        save_btn = tk.Button(self.root, text="Save Changes", 
                            font=("Arial", 12, "bold"),
                            bg="#4CAF50", fg="white",
                            width=20, height=2,
                            command=self.save_changes)
        save_btn.pack(pady=15)
        
        # Instructions
        info_label = tk.Label(self.root, 
                             text="Colors: Red → Green → Blue → Yellow → Red...",
                             font=("Arial", 9), fg="gray")
        info_label.pack()
    
    def cycle_color(self, index):
        """Cycle to the next color for the given base index."""
        current_color = self.colors[index]
        current_idx = COLORS.index(current_color)
        next_idx = (current_idx + 1) % len(COLORS)
        new_color = COLORS[next_idx]
        
        self.colors[index] = new_color
        self.buttons[index].config(bg=COLOR_DISPLAY[new_color]['hex'])
    
    def save_changes(self):
        """Save the color changes to the world file."""
        success = update_world_file(self.wbt_file, self.wbt_file, self.colors)
        
        if success:
            color_names = [COLOR_DISPLAY[c]['name'] for c in self.colors]
            message = "World file updated successfully!\n\n"
            message += "\n".join([f"Base {i+1}: {color_names[i]}" 
                                 for i in range(8)])
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", "Failed to update world file.")
    
    def run(self):
        """Start the GUI."""
        self.root.mainloop()


if __name__ == "__main__":
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"Looking for .wbt files in: {os.getcwd()}")
    
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
    
    print(f"Using world file: {input_file}")
    
    # Launch GUI
    app = ColorEditorGUI(input_file)
    app.run()