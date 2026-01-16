import os
import sys
import rclpy

current_dir = os.path.dirname(__file__)
controllers_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(controllers_dir)

from parent import ParentController

PATH_START = -0.65
SCC = 0.25 
SPP = 0.3   
SES = 0.45  
COLORS = ["red", "green", "blue", "yellow"]
SPEED = 7.0

CUBE_POSITIONS = {color: PATH_START + (i * SCC) for i, color in enumerate(COLORS)}
last_cube_x = PATH_START + (3 * SCC)
BASE_POSITIONS = {
    color: (last_cube_x + SES) + (i * SPP) for i, color in enumerate(COLORS)
}

print(f"DEBUG: Taker starting. WEBOTS_ROBOT_NAME is: {os.environ.get('WEBOTS_ROBOT_NAME')}")

class TakerController(ParentController):
    def __init__(self):
        super().__init__()
        self.camera = self.getDevice("Camera")
        if self.camera:
            self.camera.enable(self.timestep)

    def get_color(self):
        if not self.camera: return None
        image = self.camera.getImageArray()
        if not image: return None
        r, g, b = image[0][0][0], image[0][0][1], image[0][0][2]
        lower, upper = 50, 200

        if r > upper and g > upper and b > upper: return "white"
        if r < lower and g < lower and b < lower: return "black"
        if r > g and r > b: return "yellow" if g > lower else "red"
        elif g > r and g > b: return "yellow" if r > lower else "green"
        elif b > r and b > g: return "blue"
        elif r > lower and g > lower: return "yellow"
        return "unknown"

    def read_matrix_sequence(self):
        print("Reading Matrix...")
        colors = []
        last_color = "unknown"
        self.move_forward(SPEED)
        color_stable_count = 0
        current_stable_color = None

        while self.step(self.timestep) != -1:
            c = self.get_color()
            if c == current_stable_color:
                color_stable_count += 1
            else:
                color_stable_count = 0
                current_stable_color = c

            if color_stable_count > 1:
                c_valid = current_stable_color
                if c_valid in ["white", "black", "unknown", None]:
                    if len(colors) == 8 and c_valid == "white": break
                elif c_valid != last_color:
                    print(f"Found color: {c_valid}")
                    colors.append(c_valid)
                    last_color = c_valid

            if len(colors) == 8 and c == "white": break
        self.stop()
        print(f"Matrix complete: {colors}")
        return colors

    def pick_cube(self):
        print("Picking cube...")
        self.stop()
        self.set_gripper(True)
        self.set_arm_pos([-1.60, 0, 0, 0, 0])
        self.wait(20)
        self.set_arm_pos([-1.60, -1.134, -1.2, -0.82, 0])
        self.wait(80)
        self.set_gripper(False)
        self.wait(20)
        self.set_arm_pos([-1.6, -.73, -0.05, -.93, 0])
        print("Cube picked.")

    def place_cube(self):
        print("Placing cube...")
        self.stop()
        self.send_message(self.EVENT_MESSAGE)
        self.set_arm_pos([-1.6, -.73, -0.05, -.93, 0])
        self.handle_event_message()
        self.set_gripper(True)
        self.wait(10)
        self.arm_stow()
        print("Cube placed.")

    def run(self):
        self.arm_stow()
        colors = self.read_matrix_sequence()
        if len(colors) < 8:
            print("Warning: Matrix read incomplete.")
            return

        cubes_task = colors[:4]  
        bases_task = colors[4:]  

        for i in range(4):
            target_cube_color = cubes_task[i]
            target_base_color = bases_task[i]
            print(f"--- Task {i+1} ---")
            
            self.go_to_x(CUBE_POSITIONS[target_cube_color])
            self.pick_cube()
            
            # Tell Correcter which base to go to
            message = f"{self.INFO_MESSAGE}:{target_cube_color},{target_base_color}"
            self.send_message(message)
            
            self.go_to_x(BASE_POSITIONS[target_base_color])
            
            # Wait for Correcter to arrive and say "I am here"
            self.handle_event_message()
            
            self.place_cube()
            
            # Tell Correcter "I placed it, you can take it"
            self.send_message(self.EVENT_MESSAGE)

        print("All tasks placed. Waiting for Correcter to finish last move...")
        self.wait(800) # Wait ~15 seconds for Correcter to finish the last job
        print("Done.")
        
if __name__ == "__main__":
    controller = TakerController()
    try:
        controller.run()
    finally:
        controller.node.destroy_node()
        rclpy.shutdown()
