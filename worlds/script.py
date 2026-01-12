import tkinter as tk
from tkinter import ttk, messagebox
import os
import glob
import re
import shutil
import random

# Color name to RGB mapping (Webots format)
COLOR_MAP = {
    'r': '1 0 0',
    'g': '0 1 0',
    'b': '0 0 1',
    'y': '1 1 0',
}

# Color display properties for GUI
COLOR_DISPLAY = {
    'r': {'name': 'Red',    'hex': '#FF4444', 'fg': 'white'},
    'g': {'name': 'Green',  'hex': '#66BB6A', 'fg': 'black'},
    'b': {'name': 'Blue',   'hex': '#42A5F5', 'fg': 'white'},
    'y': {'name': 'Yellow', 'hex': '#FFEB3B', 'fg': 'black'},
}

# Available colors cycle
COLORS = ['r', 'g', 'b', 'y']

class WorldEditor:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def find_matching_brace(self, content, start_pos):
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

    def create_backup(self):
        """Create a .bak copy of the world file."""
        backup_path = self.file_path + ".bak"
        try:
            shutil.copy2(self.file_path, backup_path)
            return True
        except Exception as e:
            print(f"Failed to create backup: {e}")
            return False

    def update_colors(self, color_array):
        """
        Updates the Webots world file with new base colors.
        Returns (Success: bool, Message: str)
        """
        if not self.create_backup():
            return False, "Failed to create backup file. Aborting save."

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return False, f"Error reading file: {e}"

        # Robust search using regex to handle varying whitespace
        # Target: Pose { translation -1.653 0.35 0.0001
        pattern = re.compile(r'Pose\s*\{\s*translation\s+-1\.653\s+0\.35\s+0\.0001')
        match = pattern.search(content)
        
        if not match:
            return False, "Could not find the specific Base Pose block in the world file."
        
        start_pos = match.start()
        
        # Find the opening brace of this Pose block (it's inside the match, or right after)
        brace_pos = content.find('{', start_pos)
        
        # Find the matching closing brace
        end_pos = self.find_matching_brace(content, brace_pos)
        
        if end_pos == -1:
            return False, "Could not find matching closing brace in file structure."
        
        # Generate new Pose children for the 8 bases
        base_positions = [
            '0 0 0.0001', '0.12 0 0.0001', '0.24 0 0.0001', '0.36 0 0.0001',
            '0.48 0 0.0001', '0.6 0 0.0001', '0.72 0 0.0001', '0.84 0 0.0001'
        ]
        
        new_poses = []
        # Ensure we process exactly 8 bases, cycling or truncating if color_array is different
        safe_colors = (color_array * 2)[:8] 
        
        for i, color in enumerate(safe_colors):
            rgb = COLOR_MAP.get(color, '1 1 1') # Default to white if error
            pose_text = (
                f"        Pose {{\n"
                f"          translation {base_positions[i]}\n"
                f"          children [\n"
                f"            Shape {{\n"
                f"              appearance PBRAppearance {{\n"
                f"                baseColor {rgb}\n"
                f"                roughness 1\n"
                f"                metalness 0\n"
                f"              }}\n"
                f"              geometry Plane {{\n"
                f"                size 0.05 0.1\n"
                f"              }}\n"
                f"            }}\n"
                f"          ]\n"
                f"        }}"
            )
            new_poses.append(pose_text)
        
        new_children_str = '\n'.join(new_poses)
        
        # Build the replacement block
        replacement = (
            f"Pose {{\n"
            f"  translation -1.653 0.35 0.0001\n"
            f"  children [\n"
            f"    Group {{\n"
            f"      children [\n"
            f"{new_children_str}\n"
            f"      ]\n"
            f"    }}\n"
            f"  ]\n"
            f"}}"
        )
        
        new_content = content[:start_pos] + replacement + content[end_pos+1:]
        
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True, "File saved successfully."
        except Exception as e:
            return False, f"Error writing file: {e}"


class ModernColorGUI:
    def __init__(self, wbt_file):
        self.editor = WorldEditor(wbt_file)
        self.colors = ['r', 'g', 'b', 'y'] * 2 # Initial 8 colors
        self.buttons = []
        
        # UI Setup
        self.root = tk.Tk()
        self.root.title("Webots Base Color Control")
        self.root.geometry("900x450")
        self.root.resizable(False, False)
        
        self.setup_styles()
        self.build_ui()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')  # 'clam' usually allows for easier color customization
        
        # Colors
        self.bg_color = "#2c3e50"
        self.panel_color = "#34495e"
        self.text_color = "#ecf0f1"
        self.accent_color = "#27ae60"
        
        self.root.configure(bg=self.bg_color)
        
        style.configure("TFrame", background=self.bg_color)
        style.configure("Panel.TFrame", background=self.panel_color, relief="flat")
        
        style.configure("TLabel", background=self.bg_color, foreground=self.text_color, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), padding=10)
        style.configure("SubHeader.TLabel", font=("Segoe UI", 10, "italic"), foreground="#bdc3c7")
        
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=5)
        
    def build_ui(self):
        # Header Section
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", pady=(20, 10), padx=20)
        
        lbl_title = ttk.Label(header_frame, text="Base Color Controller", style="Header.TLabel")
        lbl_title.pack(side="left")
        
        lbl_file = ttk.Label(header_frame, text=f"Target: {os.path.basename(self.editor.file_path)}", style="SubHeader.TLabel")
        lbl_file.pack(side="right", anchor="se", pady=10)

        # Main Control Area
        main_panel = ttk.Frame(self.root, style="Panel.TFrame", padding=20)
        main_panel.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Color Grid
        grid_frame = ttk.Frame(main_panel, style="Panel.TFrame")
        grid_frame.pack(pady=20)
        
        for i in range(8):
            f = ttk.Frame(grid_frame, style="Panel.TFrame")
            f.grid(row=0, column=i, padx=8)
            
            # Custom Button appearance using standard tk Button for better color control than ttk
            btn = tk.Button(f, width=6, height=3, 
                            relief="flat", borderwidth=0,
                            cursor="hand2",
                            font=("Segoe UI", 12, "bold"),
                            command=lambda idx=i: self.cycle_color(idx))
            btn.pack()
            self.buttons.append(btn)
            
            lbl = ttk.Label(f, text=f"{i+1}", background=self.panel_color, font=("Segoe UI", 9, "bold"))
            lbl.pack(pady=(5, 0))
            
            self.update_button_visual(i)

        # Tools Section
        tools_frame = ttk.Frame(main_panel, style="Panel.TFrame")
        tools_frame.pack(fill="x", pady=20)
        
        # Left side tools (Batch actions)
        ttk.Label(tools_frame, text="Batch Actions:", background=self.panel_color, font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 10))
        
        ttk.Button(tools_frame, text="Randomize", command=self.randomize_colors, style="Action.TButton").pack(side="left", padx=2)
        ttk.Button(tools_frame, text="Reset", command=self.reset_colors, style="Action.TButton").pack(side="left", padx=2)
        
        # Right side tools (Save)
        save_btn = tk.Button(tools_frame, text="SAVE CHANGES", 
                             bg=self.accent_color, fg="white", 
                             font=("Segoe UI", 10, "bold"),
                             activebackground="#2ecc71", activeforeground="white",
                             relief="flat", padx=20, pady=5,
                             command=self.save)
        save_btn.pack(side="right")

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                               font=("Segoe UI", 9), foreground="#bdc3c7",
                               padding=(20, 5))
        status_bar.pack(side="bottom", fill="x")

    def update_button_visual(self, index):
        code = self.colors[index]
        props = COLOR_DISPLAY[code]
        btn = self.buttons[index]
        btn.config(bg=props['hex'], activebackground=props['hex'], fg=props['fg'], text=props['name'][0])

    def cycle_color(self, index):
        # Determine group range based on index (0-3 or 4-7)
        if 0 <= index < 4:
            start_idx, end_idx = 0, 4
        elif 4 <= index < 8:
            start_idx, end_idx = 4, 8
        else:
            return

        current_color = self.colors[index]
        next_idx_in_cycle = (COLORS.index(current_color) + 1) % len(COLORS)
        target_color = COLORS[next_idx_in_cycle]
        
        # Find which index in the same group currently holds the target color to swap with
        swap_idx = -1
        for i in range(start_idx, end_idx):
            if self.colors[i] == target_color:
                swap_idx = i
                break
        
        if swap_idx != -1:
            # Swap colors
            self.colors[index] = target_color
            self.colors[swap_idx] = current_color
            
            self.update_button_visual(index)
            self.update_button_visual(swap_idx)
            
            self.status_var.set(f"Swapped Base {index+1} with Base {swap_idx+1}")
        else:
            # Fallback (shouldn't happen if initialized correctly)
            self.colors[index] = target_color
            self.update_button_visual(index)

    def randomize_colors(self):
        # Shuffle first 4
        group1 = COLORS.copy()
        random.shuffle(group1)
        # Shuffle second 4
        group2 = COLORS.copy()
        random.shuffle(group2)
        
        self.colors = group1 + group2
        
        for i in range(8):
            self.update_button_visual(i)
        self.status_var.set("Colors randomized (maintaining uniqueness per group)")

    def reset_colors(self):
        self.colors = ['r', 'g', 'b', 'y'] * 2
        for i in range(8):
            self.update_button_visual(i)
        self.status_var.set("Colors reset to default sequence")

    def save(self):
        self.status_var.set("Saving...")
        self.root.update_idletasks()
        
        success, msg = self.editor.update_colors(self.colors)
        
        if success:
            self.status_var.set(f"Success: {msg}")
            messagebox.showinfo("Saved", f"{msg}\nBackup created successfully.")
        else:
            self.status_var.set(f"Error: {msg}")
            messagebox.showerror("Error", msg)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("Webots Base Color Tool v2.0")
    print("-" * 30)
    
    wbt_files = glob.glob("*.wbt")
    
    if not wbt_files:
        print("Error: No .wbt files found in current directory.")
        exit(1)
        
    target_file = wbt_files[0]
    if len(wbt_files) > 1:
        print("Found multiple worlds:")
        for i, f in enumerate(wbt_files):
            print(f"[{i+1}] {f}")
        try:
            sel = int(input("Select file (number): ")) - 1
            if 0 <= sel < len(wbt_files):
                target_file = wbt_files[sel]
        except ValueError:
            pass # Default to first
            
    print(f"Loading: {target_file}")
    
    app = ModernColorGUI(target_file)
    app.run()