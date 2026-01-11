from controller import Robot

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

class ParentController(Robot):
    def __init__(self):
        super(ParentController, self).__init__()
   
    def get_position(self):
        if self.gps:
            # Returns [x, y, z]
            return self.gps.getValues()
        return [0, 0, 0]

    # Done
    def set_wheels(self, v_fl, v_fr, v_bl, v_br):
        self.wheels[0].setVelocity(v_fl)
        self.wheels[1].setVelocity(v_fr)
        self.wheels[2].setVelocity(v_bl)
        self.wheels[3].setVelocity(v_br)

    # Done
    def move_forward(self, speed):
        self.set_wheels(speed, speed, speed, speed)

    # Done
    def move_backward(self, speed):
        self.set_wheels(-speed, -speed, -speed, -speed)

    # Done
    def stop(self):
        self.set_wheels(0, 0, 0, 0)

    # Done
    def set_arm_pos(self, pos_list,vel=1.2):
        for i, pos in enumerate(pos_list):
            self.arm_motors[i].setVelocity(vel)
            self.arm_motors[i].setPosition(pos)

    # Done
    def set_gripper(self, open=True):
        val = 0.025 if open else 0.0
        self.fingers[0].setPosition(val)
        self.fingers[1].setPosition(val)

    # Done
    def arm_stow(self):
        self.set_arm_pos([0, 0, 0, 0, 0])
        self.set_gripper(True)    
        
     # Done
    
    def go_to_x(self, target_x):
        current_pos = self.get_position()
        current_x = current_pos[0]

        # Determine direction
        if target_x > current_x:
            self.move_forward(SPEED)
        else:
            self.move_backward(SPEED)

        # Loop until the robot reaches the target coordinate
        while self.step(self.timestep) != -1:
            current_x = self.get_position()[0]

            # Check if we have reached or passed the target
            # We use a small threshold (0.01) to prevent jitter
            if abs(current_x - target_x) < 0.01:
                break

        self.stop()
        print(f"Arrived at X: {self.get_position()[0]:.2f}")
              
        