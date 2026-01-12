import os
import sys

# Add controllers folder to Python path
current_dir = os.path.dirname(__file__)
controllers_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(controllers_dir)

from parent import ParentController


PATH_START = -0.65
SCC = 0.25 # Space between 2 cubes
SPP = 0.3   # Space between 2 bases
SES = 0.45  # White Sapce
COLORS = ["red", "green", "blue", "yellow"]
SPEED = 5.0

last_cube_x = PATH_START + (3 * SCC)

BASE_POSITIONS = {
    color: (last_cube_x + SES) + (i * SPP) for i, color in enumerate(COLORS)
}


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

        # Got it, Thx
        self.send_message(self.EVENT_MESSAGE)
        self.wait(20)

        #self.set_arm_pos([1.60, 0, 0, 0, 0])
        #self.wait(50)

        #self.set_arm_pos([1.60, -1.134, -1.1, -0.82, 0],.9)
        #self.wait(100)

        #self.set_gripper(False)

        #for _ in range(30):
            #self.step(self.timestep)

        #self.set_arm_pos([1.60, -1.134, -1.4, -0.82, 0],.9)
        #for _ in range(30):
            #self.step(self.timestep)

        #self.set_arm_pos([1.6, 0, 0, 0, 0],0.5)
        #for _ in range(280):
            #self.step(self.timestep)


        # self.set_arm_pos([0.0, 0.6, 1.0, 1.5, 0])
        # for _ in range(280):
        #     self.step(self.timestep)

        # self.set_gripper(True)
        # for _ in range(280):
        #     self.step(self.timestep)

        # self.arm_stow()
        print("Cube placed on robot carrier.")

    def place_cube(self):
        print("Placing cube...")
        self.stop()

        self.set_arm_pos([-1.55, 1.134, 1, 0.95, 1.55],.9)
        self.wait(120)

        self.set_gripper(True)
        self.wait(10)

        # self.set_arm_pos([1.5, -1.134, -0.95, -0.89, 0],.8)
        # self.wait(140)

        # self.set_gripper(True)
        # self.wait(20)
        

        # self.set_arm_pos([0.0, 0.6, 1.0, 1.5, 0])
        # for _ in range(280):
        #     self.step(self.timestep)

        # self.set_gripper(False)
        # for _ in range(280):
        #     self.step(self.timestep)

        # self.set_arm_pos([0, 0, 0, 0, 0])
        # for _ in range(280):
        #     self.step(self.timestep)

        # self.set_arm_pos([-1.60, 0, 0, 0, 0])
        # for _ in range(20):
        #     self.step(self.timestep)

        self.arm_stow()
        print("Cube placed on its base.")    

    def run(self):

        # Hay there, I'm ready
        self.send_message(self.EVENT_MESSAGE)

        while self.step(self.timestep) != -1:

            # Got the task, and going to my dist
            message = self.handle_info_message()

            print(f"Received Tasks Need Correct : {message}")

            wrong_cube, wrong_base = message.split(",")

            print(f"Correcter needs to fix: Cube {wrong_cube} on Base {wrong_base}")

            self.go_to_x(BASE_POSITIONS[wrong_base])

            # Arrived, I'm waiting
            self.send_message(self.EVENT_MESSAGE)

            # I'll get it
            self.handle_event_message()

            self.pick_cube()

            self.go_to_x(BASE_POSITIONS[wrong_cube])
            self.place_cube()

            # Ready again
            self.send_message(self.EVENT_MESSAGE)
            self.stop()


correcter = CorrecterController()
# correcter.pick_cube()
# correcter.go_to_x(BASE_POSITIONS['green'])

correcter.run()