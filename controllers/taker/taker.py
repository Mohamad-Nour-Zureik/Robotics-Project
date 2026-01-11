from controller import Robot

PATH_START = -0.65
SCC = 0.25 # Space between 2 cubes
SPP = 0.3   # Space between 2 bases
SES = 0.45  # White Sapce
COLORS = ["red", "green", "blue", "yellow"]
SPEED = 14.0

CUBE_POSITIONS = {color: PATH_START + (i * SCC) for i, color in enumerate(COLORS)}

last_cube_x = PATH_START + (3 * SCC)

BASE_POSITIONS = {
    color: (last_cube_x + SES) + (i * SPP) for i, color in enumerate(COLORS)
}

print("Cube Positions:", CUBE_POSITIONS)
print("Base Positions:", BASE_POSITIONS)


class TakerController(Robot):
    # Done
    def __init__(self):
        super(TakerController, self).__init__()
        self.timestep = int(self.getBasicTimeStep())

        # Camera Initialization
        self.camera = self.getDevice("Camera")

        if self.camera:
            self.camera.enable(self.timestep)
        else:
            print("Error: Camera not found")

        # --- NEW: Emitter Initialization (Sender) ---
        self.emitter = self.getDevice("emitter")
        # Ensure we are broadcasting on a specific channel (e.g., 1)
        # The Correcter must have a Receiver set to the same channel.
        if self.emitter:
            self.emitter.setChannel(1)

        # GPS Initialization
        self.gps = self.getDevice("gps")  # Ensure the name matches the .wbt file
        if self.gps:
            self.gps.enable(self.timestep)
        else:
            print(
                "Error: GPS device not found. Add a GPS node to your robot in the scene tree."
            )

        # Wheels
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

        # Arm
        self.arm_motors = []
        for i in range(1, 6):
            motor = self.getDevice("arm" + str(i))
            self.arm_motors.append(motor)

        # Gripper
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
    def get_color(self):
        if not self.camera:
            return None

        image = self.camera.getImageArray()
        if not image:
            return None

        r = image[0][0][0]
        g = image[0][0][1]
        b = image[0][0][2]

        lower = 50
        upper = 200

        if r > upper and g > upper and b > upper:
            return "white"
        if r < lower and g < lower and b < lower:
            return "black"

        if r > g and r > b:
            if g > lower:
                return "yellow"
            return "red"
        elif g > r and g > b:
            if r > lower:
                return "yellow"
            return "green"
        elif b > r and b > g:
            return "blue"
        elif r > lower and g > lower:
            return "yellow"

        return "unknown"

    # Done
    def read_matrix_sequence(self):
        print("Reading Matrix...")
        colors = []
        last_color = "unknown"

        self.move_forward(SPEED)

        color_stable_count = 0
        current_stable_color = None

        while self.step(self.timestep) != -1:
            c = self.get_color()

            # Simple de-bounce logic
            if c == current_stable_color:
                color_stable_count += 1
            else:
                color_stable_count = 0
                current_stable_color = c

            if color_stable_count > 1:  # Stable for ~100ms
                c_valid = current_stable_color

                if c_valid in ["white", "black", "unknown", None]:
                    if len(colors) == 8 and c_valid == "white":
                        break
                elif c_valid != last_color:
                    print(f"Found color: {c_valid}")
                    colors.append(c_valid)
                    last_color = c_valid

            if (
                len(colors) == 8 and c == "white"
            ):  # Immediate break if white seen after 8
                break

        self.stop()
        print(f"Matrix complete: {colors}")
        return colors

    # Done
    def pick_cube(self):
        print("Picking cube (Stationary Base)...")
        self.stop()

        self.set_gripper(True)

        self.set_arm_pos([-1.60, 0, 0, 0, 0])
        for _ in range(50):
            self.step(self.timestep)

        self.set_arm_pos([-1.60, -1.134, -1.2, -0.82, 0],.9)
        for _ in range(100):
            self.step(self.timestep)

        self.set_gripper(False)
        for _ in range(30):
            self.step(self.timestep)

        self.set_arm_pos([-1.6, 0, 0, 0, 0],0.5)
        # for _ in range(280):
        #     self.step(self.timestep)

        # self.set_arm_pos([0.0, 0.6, 1.0, 1.5, 0])
        # for _ in range(280):
        #     self.step(self.timestep)

        # self.set_gripper(True)
        # for _ in range(280):
        #     self.step(self.timestep)

        # self.arm_stow()
        print("Cube placed on robot carrier.")

    # Done
    def move_right_to_place_cube(self, steps, speed):
        self.move_right(speed)

        for _ in range(steps):
            self.step(self.timestep)

        self.stop()

    # Done
    def move_back_after_placing_the_cube(self, steps, speed):
        self.move_left(speed)

        for _ in range(steps):
            self.step(self.timestep)

        self.stop()

    # Done
    def place_cube(self):
        steps = 150
        speed = 2.0
        print("Placing cube...")
        self.stop()

        self.move_right_to_place_cube(steps=steps, speed=speed)

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

        self.set_arm_pos([-1.60, -1.134, -1.2, -0.82, 0],.8)
        for _ in range(100):
            self.step(self.timestep)

        self.set_gripper(True)
        for _ in range(20):
            self.step(self.timestep)

        self.arm_stow()
        print("Cube placed on its base.")

        self.move_back_after_placing_the_cube(steps=steps, speed=speed)

    def move_to_with_speed(self,dir,speed):
        # Determine direction
        if dir:
            self.move_forward(speed)
        else:
            self.move_backward(speed)
        

    # Done
    def go_to_x(self, target_x):
        current_pos = self.get_position()
        current_x = current_pos[0]
        init_x = current_x

        dir = target_x > current_x

        # Loop until the robot reaches the target coordinate
        while self.step(self.timestep) != -1:
            current_x = self.get_position()[0]

            speed = SPEED * min(
                1,
                0.06 + (abs(current_x - init_x) * 7) ** 2, # for the taking off 
                0.06 + (abs(current_x - target_x) * 7)** 2 # for the slowing down
            )
            
            self.move_to_with_speed(dir,speed)

            # Check if we have reached or passed the target
            # We use a small threshold (0.01) to prevent jitter
            if abs(current_x - target_x) < 0.01:
                break

        self.stop()
        print(f"Arrived at X: {self.get_position()[0]:.2f}")

    # Done
    def run(self):
        self.arm_stow()

        colors = self.read_matrix_sequence()

        self.go_to_x(PATH_START)

        if len(colors) < 8:
            print("Warning: Matrix read incomplete.")
            return

        cubes_task = colors[:4]  
        bases_task = colors[4:]  

        for i in range(4):
            target_cube_color = cubes_task[i]
            target_base_color = bases_task[i]

            print(f"--- Task {i+1} ---")
            print(f"Goal: Pick {target_cube_color} cube -> Place on {target_base_color} base")

            cube_x = CUBE_POSITIONS[target_cube_color]
            print(f"Moving to cube {target_cube_color} at X={cube_x}")
            self.go_to_x(cube_x)

            self.pick_cube()

            base_x = BASE_POSITIONS[target_base_color]
            print(f"Moving to base {target_base_color} at X={base_x}")
            self.go_to_x(base_x)

            self.place_cube()

            if target_cube_color != target_base_color:
                message = f"{target_cube_color},{target_base_color}"

                print(f"(!) Different detected. Sending data to Correcter: {message}")

                if self.emitter:
                    self.emitter.send(message.encode("utf-8"))

        print("All tasks completed successfully!")


controller = TakerController()
controller.run()
