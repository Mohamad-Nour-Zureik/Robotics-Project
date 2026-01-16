import os
import sys
import rclpy

current_dir = os.path.dirname(__file__)
controllers_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(controllers_dir)

from parent import ParentController

PATH_START = -0.65
SCC = 0.25 
SPP = 0.3   
SES = 0.45  
COLORS = ["red", "green", "blue", "yellow"]
SPEED = 5.0

last_cube_x = PATH_START + (3 * SCC)
BASE_POSITIONS = {
    color: (last_cube_x + SES) + (i * SPP) for i, color in enumerate(COLORS)
}

print(f"DEBUG: Correcter starting. WEBOTS_ROBOT_NAME is: {os.environ.get('WEBOTS_ROBOT_NAME')}")

class CorrecterController(ParentController):
    def __init__(self):
        super().__init__()

    def pick_cube(self):
        print("Picking cube from wrong Base...")
        self.stop()
        self.set_gripper(True)
        self.set_arm_pos([-1.55,.7,.4,0.37,1.55])
        self.wait(150)
        self.set_gripper(False)
        self.wait(20)
        self.send_message(self.EVENT_MESSAGE)
        self.wait(20)
        print("Cube picked.")

    def place_cube(self):
        print("Placing cube...")
        self.stop()
        self.set_arm_pos([-1.55, 1.134, 1, 0.95, 1.55],.9)
        self.wait(120)
        self.set_gripper(True)
        self.wait(10)
        self.arm_stow()
        print("Cube placed.")  


    def run(self):
        while self.step(self.timestep) != -1:
            message = self.handle_info_message()
            print(f"Received Tasks Need Correct : {message}")
            wrong_cube, wrong_base = message.split(",")
            print(f"Correcter needs to fix: Cube {wrong_cube} on Base {wrong_base}")

            self.go_to_x(BASE_POSITIONS[wrong_base])

            # This is the ONLY time we send an event: "I am here, give me the cube"
            self.send_message(self.EVENT_MESSAGE)

            self.handle_event_message()  # Wait for Taker to place it
            self.pick_cube()

            self.go_to_x(BASE_POSITIONS[wrong_cube])
            self.place_cube()

            # REMOVED FINISH MESSAGE HERE (To prevent Taker from starting the next drop too early)
            self.stop()


if __name__ == "__main__":
    correcter = CorrecterController()
    try:
        correcter.run()
    finally:
        correcter.node.destroy_node()
        rclpy.shutdown()
