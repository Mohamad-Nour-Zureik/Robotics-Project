from controller import Robot

PATH_START = -0.65
STARTING_POINT = 2.15
SCC = 0.25 # Space between 2 cubes
SPP = 0.3   # Space between 2 bases
SES = 0.45  # White Sapce
COLORS = ["red", "green", "blue", "yellow"]
SPEED = 5.0

last_cube_x = PATH_START + (3 * SCC)

BASE_POSITIONS = {
    color: (last_cube_x + SES) + (i * SPP) for i, color in enumerate(COLORS)
}

class CorrecterController(Robot):
    def __init__(self):
        super(CorrecterController, self).__init__()
        self.timestep = int(self.getBasicTimeStep())

        # Receiver Initialization ------------------------------
        self.receiver = self.getDevice("receiver")
        self.receiver.enable(self.timestep)
        self.receiver.setChannel(1)
        
        
        # GPS Initialization -----------------------------------
        self.gps = self.getDevice("gps")  # Ensure the name matches the .wbt file
        if self.gps:
            self.gps.enable(self.timestep)
        else:
            print(
                "Error: GPS device not found. Add a GPS node to your robot in the scene tree."
            )

        
        # Wheels -----------------------------------------------
        self.wheels = []
        # Mapping:
        # fl (Front Left)  -> wheel2
        # fr (Front Right) -> wheel1
        # bl (Back Left)   -> wheel4
        # br (Back Right)  -> wheel3
        wheel_names = ["wheel2", "wheel1", "wheel4", "wheel3"]

        for name in wheel_names:
            wheel = self.getDevice(name)
            if wheel:
                wheel.setPosition(float("inf"))
                wheel.setVelocity(0.0)
                self.wheels.append(wheel)
            else:
                print(f"Error: Wheel {name} not found")

        # Check if we found all wheels
        if len(self.wheels) != 4:
            print("Error: Could not find all wheels!")
            
        # Arm ---------------------------------------------------
        self.arm_motors = []
        for i in range(1, 6):
            motor = self.getDevice("arm" + str(i))
            self.arm_motors.append(motor)

        # Gripper ------------------------------------------------
        self.fingers = []
        for name in ["finger::left", "finger::right"]:
            gripper = self.getDevice(name)
            self.fingers.append(gripper)
        
        
     # Done
   
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
              
    def pick_cube(self):
        print("Picking cube from wrong Base...")
        self.stop()

        self.set_gripper(True)

        self.set_arm_pos([1.60, 0, 0, 0, 0])
        for _ in range(50):
            self.step(self.timestep)

        self.set_arm_pos([1.60, -1.134, -1.1, -0.82, 0],.9)
        for _ in range(100):
            self.step(self.timestep)

        self.set_gripper(False)
        for _ in range(30):
            self.step(self.timestep)
        
        self.set_arm_pos([1.60, -1.134, -1.4, -0.82, 0],.9)
        for _ in range(30):
            self.step(self.timestep)

        self.set_arm_pos([1.6, 0, 0, 0, 0],0.5)
        for _ in range(280):
            self.step(self.timestep)

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

        # self.set_gripper(True)

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

   
        self.set_arm_pos([1.5, -1.134, -0.9, -0.82, 0],.8)
        for _ in range(100):
            self.step(self.timestep)

        self.set_gripper(True)
        for _ in range(20):
            self.step(self.timestep)

        self.arm_stow()
        print("Cube placed on its base.")    
    
    
    
    def run(self):
        
        while self.step(self.timestep) != -1:
            if self.receiver.getQueueLength() > 0:
                message = self.receiver.getString() # .decode("utf-8")
                self.receiver.nextPacket() 
                
                print(f"Received Tasks Need Correct : {message}")

                wrong_cube, wrong_base = message.split(",")

                print(f"Correcter needs to fix: Cube {wrong_cube} on Base {wrong_base}")
                
                self.go_to_x(BASE_POSITIONS[wrong_base])
                self.pick_cube()
                self.go_to_x(BASE_POSITIONS[wrong_cube])
                self.place_cube()

                self.stop()
                



correcter = CorrecterController()
correcter.run()
