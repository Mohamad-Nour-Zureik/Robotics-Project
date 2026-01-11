from controller import Robot


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
        
        
    def run(self):
        while self.step(self.timestep) != -1:
            if self.receiver.getQueueLength() > 0:

                message = self.receiver.getString() # .decode("utf-8")
                self.receiver.nextPacket() 

                print(f"Received Tasks Need Correct : {message}")

                wrong_cube, wrong_base = message.split(",")

                print(f"Correcter needs to fix: Cube {wrong_cube} on Base {wrong_base}")



correcter = CorrecterController()
correcter.run()
