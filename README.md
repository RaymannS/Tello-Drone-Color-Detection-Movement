# Read Me for Tello Drone Color Detection Movement code
This program will allow the Tello Drone to use the front camera to detect a multi-colored target and then calculate the distance to the target and land on it.
## Status
### [Released]
## Creator: Raymann Singh
### Created: 2022.11.28
## Last Editor: R. Singh
### Last Edited: 2023.1.27

## How to Use
Download the [Drone Visual Detection Code.py](https://github.com/RaymannS/Tello-Drone-Color-Detection-Movement/blob/main/Drone%20Visual%20Detection%20Code.py) file and open it in python or visual studio code.
Download all required libraries at the top of the code (cv2, numpy, and djitellopy).
In the code there are multiple variables that can be changed to determine the take off conditions, when hitting run on the code it will prompt for an input: "t" will start the visual detection for the Drone while "f" will start the code for a computer camera.
The Drone will then take off and scan for a target, after a fixed amount of time it will move forward and then rotate to scan for the target. The Target's colors can be maniuplated in the code. After the code is ran the Drone will turn off and the code will terminate.

### Bugs and updates
#### [0.1.1] - 2023.1.27 
Tidied up code for inital commit to Github
#### [0.1.0] - 2022.12.2
Final Launch
