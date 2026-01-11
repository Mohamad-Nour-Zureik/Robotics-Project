from controller import Robot


SPEED = 5.0

class ParentController(Robot):
    def __init__(self):
        super(ParentController, self).__init__()
        self.timestep = int(self.getBasicTimeStep())

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
    def move_left(self, speed):
        # fl , fr , bl , br
        self.set_wheels(-speed, speed, speed, -speed)

    # Done
    def move_right(self, speed):
        self.set_wheels(speed, -speed, -speed, speed)

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
