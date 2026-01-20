# Steps to Run the Project :

## In case you have ros2 and webots at the same host:
### Source the setup of ros in terminal :
replace {ROS_DISTRO} with your installed distro, jazzy worked properly.

```bash
source /opt/ros/{ROS_DISTRO}/setup.zsh
webots 
```

### Run the script in another termainal : 
```bash
./run.sh
```


## In case you have webots at host and want to link it with ros2 in a docker container

1. Clone the project
```bash
git clone https:\\github.com\Mohamad-Nour-Zureik/Robotics-Project
```
2. Run your ros image with this command:
```bash
docker run -it --name ros2 --network host -v ./Robotics-Project:/project ros:latest
```
This command with create the container with name ros2 and shares the same network with the host machine (So webots and ros can communicate with each other over *TCP*) and create a shares the project directory with the container at `/project`
At the year of developing the repo, Ros2 Jazzy was the latest LTS and was the latest image available, also ros:humble was tested and worked correctly

3. Inside the container: Update and install webots-ros2
```bash
apt update

apt install ros-$ROS_DISTRO-webots-ros2
```

4. Install webots inside the container. (This step is over, since all it did is to configure some webots main libraries and dependencies that for me was too late to share it from my host :)_BTW now you can use webots from inside the container with if those flags was set in the container creating step `-e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix` and enabled xhost with `xhost +local:root` to let the container to use xserver0_)

```bash
# Download the Webots GPG key and save it to the /etc/apt/keyrings/ directory using gpg and curl (or wget).
curl -fsSL https://cyberbotics.com/Cyberbotics.asc | gpg --dearmor -o /etc/apt/keyrings/cyberbotics.gpg

# Add the Webots repository to your APT sources list with a Signed-By reference to the key you just added.
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/cyberbotics.gpg] https://cyberbotics.com/debian/ binary-amd64/" | tee /etc/apt/sources.list.d/webots.list > /dev/null

# then install webots:
apt update; apt install webots -y
```

By now you are ready to deal with ros and reflect changes to webots, So run webots at host, it will automatically creates a TCP over localhost with port 1234, and ROS2 can communicate with it over this link, So final:

5. Run the script inside `/project` directory, (make sure its executable by `chmod +x ./project/run.sh`, it should be already executable since git can track it at least at the tested env)
```bash
./project/run.sh
```
---
### **Quick inspection checklist while the simulation is running**
you can make some other logs and display some info like:

1. **Check nodes are registered**

   ```bash
   ros2 node list
   ```

2. **Check which topics exist**

   ```bash
   ros2 topic list -t
   ```

3. **Check message flow on a topic**

   ```bash
   ros2 topic echo /robot_comm
   ```

4. **Check topic details**

   ```bash
   ros2 topic info /robot_comm --verbose
   ```

5. **Check how often messages are sent**

   ```bash
   ros2 topic hz /robot_comm
   ```

Those commands let you *discover what your packages are actually doing* at runtime — which is critical for debugging your multi-robot communication logic.