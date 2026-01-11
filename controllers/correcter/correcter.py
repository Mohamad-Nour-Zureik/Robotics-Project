from controller import Robot


class CorrecterController(Robot):
    def __init__(self):
        super(CorrecterController, self).__init__()
        self.timestep = int(self.getBasicTimeStep())

        # Receiver Initialization
        self.receiver = self.getDevice("receiver")
        self.receiver.enable(self.timestep)
        self.receiver.setChannel(1)

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
