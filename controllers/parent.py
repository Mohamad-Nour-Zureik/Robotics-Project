import sys
import os
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from controller import Robot
import collections

current_dir = os.path.dirname(__file__)
controllers_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(controllers_dir)
SPEED = 14.0

class ParentController(Robot):
    def __init__(self):
        super(ParentController, self).__init__()

        self.EVENT_MESSAGE = "EVNT"
        self.INFO_MESSAGE = "INFO"

        self.timestep = int(self.getBasicTimeStep())
        # --- FIX: Use 'robot_name' to avoid conflict with built-in 'name' property ---
        self.robot_name = self.getName()
        # --- ROS 2 INITIALIZATION ---
        if not rclpy.ok():
            rclpy.init(args=None)

        # Create a unique node name based on the robot name (sanitized)
        sanitized_name = "".join(x for x in self.robot_name if x.isalnum() or x == "_")
        self.node = rclpy.create_node(sanitized_name)

        # Create Publisher and Subscriber on a shared topic
        self.pub = self.node.create_publisher(String, "/robot_comm", 10)
        self.sub = self.node.create_subscription(
            String, "/robot_comm", self._ros_callback, 10
        )

        # Message Queue to replicate Receiver behavior
        self.msg_queue = collections.deque()

        # GPS Initialization
        self.gps = self.getDevice("gps")
        if self.gps:
            self.gps.enable(self.timestep)
        else:
            print("Error: GPS device not found.")

        # Wheels Initialization
        self.wheels = []
        wheel_names = ["wheel2", "wheel1", "wheel4", "wheel3"]
        for name in wheel_names:
            wheel = self.getDevice(name)
            if wheel:
                wheel.setPosition(float("inf"))
                wheel.setVelocity(0.0)
                self.wheels.append(wheel)
            else:
                print(f"Error: Wheel {name} not found")

        # Arm & Gripper Initialization
        self.arm_motors = []
        for i in range(1, 6):
            self.arm_motors.append(self.getDevice("arm" + str(i)))

        self.fingers = []
        for name in ["finger::left", "finger::right"]:
            self.fingers.append(self.getDevice(name))

    # --- ROS 2 CALLBACK & HELPERS ---
    def _ros_callback(self, msg):
        # Parse format: "SENDER_NAME|CONTENT"
        try:
            sender, content = msg.data.split("|", 1)
            if sender != self.robot_name:  # Ignore own messages
                self.msg_queue.append(content)
        except ValueError:
            pass  # Malformed message

    def step_and_spin(self):
        # Advance simulation AND process ROS callbacks
        ret = self.step(self.timestep)
        if ret != -1:
            rclpy.spin_once(self.node, timeout_sec=0)
        return ret

    def send_message(self, message):
        print(f"From {self.robot_name}, Sending message {message}")
        # Payload includes sender name for filtering
        payload = f"{self.robot_name}|{message}"
        self.pub.publish(String(data=payload))

    def handle_event_message(self):
        print(f"{self.robot_name} is waiting for EVENT...")
        while self.step_and_spin() != -1:
            if self.msg_queue:
                # Peek/Pop logic matching original
                message = self.msg_queue[0]  # Peek
                if message.startswith(self.EVENT_MESSAGE):
                    self.msg_queue.popleft()  # Consume
                    return True
                # If message is not EVNT, maybe wait or consume?
                # Original logic implied strict ordering or filtering.
                # We will leave it in queue if it's not what we want (simplistic)
                # OR simplistic assumption: only relevant msgs arrive.
                # Let's assume we consume it if it's the wrong type to prevent deadlock,
                # but print warning.
                if not message.startswith(self.EVENT_MESSAGE):
                    # Just skip unrelated messages?
                    self.msg_queue.popleft()

    def handle_info_message(self):
        print(f"{self.robot_name} is waiting for INFO...")
        while self.step_and_spin() != -1:
            if self.msg_queue:
                message = self.msg_queue.popleft()
                if message.startswith(self.INFO_MESSAGE):
                    return message[len(self.INFO_MESSAGE) + 1 :]

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
    def wait(self, rng):
        for _ in range(rng):
            self.step(self.timestep)

    def move_by_direction(self, dir, speed = SPEED):
        if dir:
            self.move_forward(speed)
        else:
            self.move_backward(speed)

    def go_to_x(self, target_x):
        current_pos = self.get_position()
        current_x = current_pos[0]
        init_x = current_x

        if abs(target_x - current_x) <= 0.01:
            return

        # Determine direction
        dir = target_x - current_x > 0.01

        # Loop until the robot reaches the target coordinate
        while self.step(self.timestep) != -1:
            current_x = self.get_position()[0]

            speed = SPEED * min(
                1,
                0.07 + (4.5 * abs(current_x - target_x)) ** 2,
                0.07 + (4.5 * abs(current_x - init_x)) ** 2,
            )

            self.move_by_direction(dir, speed)

            if abs(current_x - target_x) <= 0.001 or dir != (target_x - current_x > 0.01):
                break

        self.stop()
        print(f"Arrived at X: {self.get_position()[0]:.2f}")
