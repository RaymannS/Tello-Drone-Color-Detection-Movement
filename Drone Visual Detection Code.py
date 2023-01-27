import cv2
import numpy as np
from djitellopy import Tello
import math, time, os

os.system('cls')

#Hue, Saturation, Value

# lower mask (0-10)
lower_red1 = np.array([0,70,40])
upper_red1 = np.array([5,255,255]) # Changed from 10 to 5

# upper mask (170-180)
lower_red2 = np.array([170,70,40]) # Try 136, 87, 111
upper_red2 = np.array([179,255,255])

# Pink
lower_pink = np.array([140,50,20])
upper_pink = np.array([179,255,255])

# orange
lower_orange = np.array([5, 60, 60])
upper_orange = np.array([15, 255, 255])

# Upper and Lower for Blue
lower_blue = np.array([80,40,20]) # Try 94, 80, 2 ---- changed from 90, 50, 40  130, 255, 255
upper_blue = np.array([130,255,255])

# Upper and lower for purple
lower_purple = np.array([129,50,70])
upper_purple = np.array([158,255,255])

# Upper and lower for green
lower_green = np.array([25, 52, 72])
upper_green = np.array([102, 255, 255])

####################### Final target GREEN AND BLUE ##################################

tello = Tello()
state = input("Drone? t(Drone) or f(Camera)\n")

if state == "t":
    state = True
    wall = False
    tello.connect()
    tello.streamon()
elif state == "f":
    state = False
    wall = False
elif state == "tt":
    state = True
    wall = True
    wallHeightInput = input("")
    wallHeightInput = int(wallHeightInput)
    tello.connect()
    tello.streamon()

checkPID = False
yawFlag = False
fbFlag = False
hFlag = False
PID = [0.175, 0, 0.05] # 0.12, 0.0049, 0.001
PIDFB = [1, 0, 0.1]
PIDH = [0.12, 0, 0.01]
prevTime = 0
prevErrX = 0
prevErrFB = 0
prevErrH = 0
targetLineDistance = 0
counterLiveFeed = 0
count = 0
rotate = 0
counter = 0
errorFreeze = 0
lastError = 0
integral = 0
Fv = 972
perfectTime = 100000000000 # first time yaw was perfect
detectionCounter = 0
nonTargetTime = 1110987654321
landed = True
shutOff = False
distance = mpx = mpy = cx = cy = Di = x = y = w = h = x2 = y2 = w2 = h2 = 0
flag = False
targetDetected = False
mpCounter = False

if not state:
    video = cv2.VideoCapture(0)
tookoff = False

def distVideo():
    global video, targetDetected, Di, checkPID, x, y, w, h, x2, y2, w2, h2, dt, Fv, F
    global mpx, mpy, cx, cy, distance, img, prevTime, prevErrX, PID, landed, targetLineDistance, distancey, yawFlag, hFlag, fbFlag
    global prevErrX, pythagorean, heightTarget, prevErrFB, PIDFB, PIDH, circleDetected, tookoff, prevErrH, mpCounter, counterLiveFeed, screenheight, screenwidth
    
    if state:
        img = tello.get_frame_read().frame
    else:
        valid, img = video.read()
        if not valid:
            print("Image failed")
            #break
            return
    image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # mask21 = cv2.inRange(image, lower_red1, upper_red1)
    # mask22 = cv2.inRange(image, lower_red2, upper_red2)
    # mask = cv2.medianBlur(mask21 + mask22, 5)
    mask = cv2.inRange(image,lower_pink,upper_pink)
    mask = cv2.medianBlur(mask, 5)
    # mask = cv2.inRange(image,lower_green,upper_green)
    # mask = cv2.medianBlur(mask, 5)
    mask2 = cv2.inRange(image, lower_blue, upper_blue)
    mask2 = cv2.medianBlur(mask2, 5)


    contours, heirarchy = cv2.findContours(mask,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours2, heirarchy2 = cv2.findContours(mask2,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    screenwidth = img.shape[1]
    screenheight = img.shape[0]
    cx = math.ceil((screenwidth)/2)
    cy = math.ceil((screenheight)/1.3) # center x and y
    circleDetected = False
    circle2Detected = False
    x = y = w = h = x1 = y1 = w1 = h1 = distance = x2 = y2 = w2 = h2 = mp2 = mpx = mpy = mpx2 = mpy2 = i = j = 0
    centers1 = []
    centers2 = []

    if len(contours) != 0:
        for contour in contours:
            c = max(contours, key = cv2.contourArea)
            if cv2.contourArea(contour) > 200:
                circleDetected = True
                x1, y1, w1, h1 = cv2.boundingRect(contour)
                mpx1 = math.ceil(((x1+w1/2)))
                mpy1 = math.ceil(((y1+h1/2))) # midpoint of object
                
                cv2.rectangle(img, (x1,y1), (x1+w1, y1+h1), (0, 255, 255), 3)
                cv2.circle(img, (cx,cy), 25, (0,255,255), 2) # center circle @ target
                cv2.circle(img, (mpx,mpy), 5, (0, 255, 255), 2) # center circle of object
                #cv2.line(img, (cx,cy), (mpx,mpy), (230,230, 250), 1) # line in between
                centers1.append([mpx1, mpy1, w1, x1])

    if len(contours2) != 0:
        for contour2 in contours2:
            c2 = max(contours2, key = cv2.contourArea)
            if cv2.contourArea(contour2) > 500: #and cv2.contourArea(contour2) < 15000:
                circle2Detected = True
                x2, y2, w2, h2 = cv2.boundingRect(contour2)
                mpx2 = math.ceil(((x2+w2/2)))
                mpy2 = math.ceil(((y2+h2/2))) # midpoint of object

                cv2.rectangle(img, (x2,y2), (x2+w2, y2+h2), (0, 255, 0), 3)
                cv2.circle(img, (mpx2,mpy2), 5, (0, 255, 0), 2) # center circle of object
                #cv2.line(img, (cx,cy), (mpx2,mpy2), (150,150,0), 1) # line in between
                centers2.append([mpx2, mpy2, w2])

    
    if len(contours) != 0 or len(contours2) != 0:            
        for i in range(len(centers1)):
            for j in range(len(centers2)): 
                try:
                    targetLineDistance = round(math.sqrt((centers1[i][0]-centers2[j][0])**2 + (centers1[i][1]-centers2[j][1])**2))
                    if targetLineDistance <= 10 and targetLineDistance >= 0:
                        targetDetected = True
                        mpx = centers1[i][0]
                        mpy = centers1[i][1]
                        w = centers1[i][2]
                        x = centers1[i][3]
                        cv2.putText(img, "Target", (mpx,mpy), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        cv2.line(img, (mpx,mpy), (cx,cy), (0,255,0), 3)
                        break 
                    else:
                        targetDetected = False
                        mpx = mpy = x = w = 0
                except:
                    print("Target Line Distance Exception")
                    trash = 0
            if targetDetected and w1 != 0:
                #print("Target Detected")
                break
            else:
                targetDetected = False

    D = 30.48 # distance in cm for 1 ft
    W = 16 # change this to the marker width in cm
    F = round((w1*D)/W) # at 1 ft what is this value and change Fv
    #cv2.putText(img,str(F),(300,300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    
    if targetDetected and w != 0:
        #print("Target Detected - Doing Distance")
        Di = round((W*Fv)/w)
        distance = round(abs(cx-mpx))
        distancey = round(abs(cy-mpy))
        text ='Distance away: ' + str(Di) + 'cm'
        text2 = 'Line Dist: ' + str(distance) + 'pixels'
        TEXT = 'Center Dist: ' + str(targetLineDistance) + 'pixels'
        cv2.putText(img, text, (25,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(img, text2, (25,60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(img, TEXT, (25,95), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    if state:
        Fv = 900 #972 --- 947 -- 900 was perfect
        # if overshoot decrease?
        # if undershoot increase?
    else:
        Fv = 646 # 646 for laptop cam 840 for drone 
    
    detection()
    
    if state and not targetDetected and mpCounter:
        asdads = 3
    
    if checkPID: 
        dt = (time.time() - prevTime)
        prevTime = time.time()
        #print("Doing PID", dt)
        errPowerFB = fbPID()
        errPowerYaw = yawPID()
        errPowerH = hPID()

        pidText = "Fb: " + str(errPowerFB) + " Yaw: " + str(errPowerYaw) + " H: " + str(errPowerH)
        cv2.putText(img, pidText, (25, screenheight - 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if tookoff:   
            doPID()      

    #cv2.imshow("pink", mask)
    #cv2.imshow("blue", mask2)
    cv2.imshow("live feed", img)
    
    if counterLiveFeed == 0:
        cv2.moveWindow("live feed", 20,20)
        counterLiveFeed = 1
    cv2.waitKey(1)
    if targetDetected and w != 0:
        pythagorean = checkTrig()
        return pythagorean


def checkTrig():
    global heightTarget
    if state:
        currentHeight = tello.get_distance_tof()
    else:
        currentHeight = 150
    tableHeight = 70.485
    heightTarget = currentHeight - tableHeight 
    pythagorean = round(math.sqrt(Di**2 - heightTarget**2))
    #print("Got pythagorean", pythagorean, "and got Fv", Fv)
    return pythagorean

def detection():
    global Di, img, distancey, count, distance, flag, checkPID, mpCounter, prevErrX, perfectTime, nonTargetTime, detectionCounter
    minPixel = 20 # minimum pixel amount for detection
    if nonTargetTime == 1110987654321: # Total nonTargetTime should not be returning to this number
        nonTargetTime = time.time()
    if targetDetected and w != 0 and abs(prevErrX) <= minPixel:
        cv2.putText(img, "Both Correct", (25,130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if (perfectTime == 100000000000):
            perfectTime = time.time()
            #print("Perfect Time set to ", perfectTime)
        print("Perfect Time", time.time() - perfectTime)
        if (time.time() - perfectTime > 2.2):
            perfectTime = 100000000000
            #print(perfectTime)
        if (time.time() - perfectTime > 2):
            print("ready-------------------")
            flag = True
    elif targetDetected and w != 0 and abs(prevErrX) > minPixel:
        cv2.putText(img, "Not matching up", (25,130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        flag = False
        perfectTime = 100000000000
        #print("Perfect Time set to ", perfectTime, " in line 261")

    if targetDetected and not flag:
        checkPID = True
        mpCounter = True # Target has been detected atleast once
    elif not targetDetected and prevErrX == 0:
        checkPID = False
        perfectTime = 100000000000

    if state and not targetDetected and detectionCounter == 0 and (time.time() - nonTargetTime > 10):
        detectionCounter = 1
        tello.send_rc_control(0,0,0,0)
        time.sleep(3)
        tello.move_forward(round(3.55*12*2.54))
        time.sleep(4)
        tello.rotate_clockwise(180)
        time.sleep(3)
    if state and not targetDetected and detectionCounter == 0 and (time.time() - nonTargetTime > 3) and (time.time() - nonTargetTime < 7):
        tello.send_rc_control(0,0,0,0)
        print("Not locked on, sending ZERO")

def yawPID():
    global errorFreeze, lastError
    global x, w, screenwidth, dt, prevErrX, integral
    errorFreeze = errorFreeze + 1
    if w != 0:
        midX = x + (w/2)
        errX = screenwidth/2-midX 
        
        if (errorFreeze > 10 == 0):
            errorFreeze = 0
            if (lastError == errX):
                print("Frozen")
                return 0
            lastError = errX

        dErrX = (errX-prevErrX)/dt
        prevErrX = errX
        integral = integral + PID[1]*dt*errX
        if errX == 0:
            integral = 0
        
        errPowerYaw = PID[0]*errX + integral + PID[2]*dErrX
        errPowerYaw = errPowerYaw * -1
        errPowerYaw = round(errPowerYaw)
        print(round(errX,2), errPowerYaw, "[", round(PID[0]*errX,2), round(integral,2), round(PID[2]*dErrX,2), "]", "   ", PID)
        if errPowerYaw > 20:
            errPowerYaw = 20
            integral = 0
        elif errPowerYaw < -20:
            errPowerYaw = -20
            integral = 0
        return errPowerYaw

def fbPID():
    global Di, dt, prevErrFB
    if Di != 0:
        targetD = 90
        errFB = Di-targetD
        dDist = (prevErrFB-errFB)/dt
        prevErrFB = errFB
        errPowerFB = round(PIDFB[0]*errFB + PIDFB[2]*dDist)
        if errPowerFB > 30:
            errPowerFB = 30
        elif errPowerFB < -30:
            errPowerFB = -30
        return errPowerFB
    else:
        return 0

def hPID():
    global screenheight, mpy, dt, prevErrH
    if mpy != 0:
        errH = screenheight/1.3 - mpy
        dErrH = (prevErrH-errH)/dt
        prevErrH = errH
        errPowerH = round(PIDH[0]*errH + PIDH[2]*dErrH)
        if errPowerH > 20:
            errPowerH = 20
        elif errPowerH < -20:
            errPowerH = -20
        return errPowerH
    else:
        return 0

def doPID():
    global checkPID, flag
    if w != 0:
        tello.send_rc_control(0,0,0,yawPID())

def doFirstObstacle(wallHeight):
    if state:
        # If there is a wall
        time.sleep(3)
        tello.move_up(wallHeight)
        time.sleep(4)
        tello.move_forward(wallHeight + 80)
        time.sleep(4)
        tello.move_down(round(80))
        time.sleep(3)

def lastMove():
    time.sleep(2.25)
    tello.takeoff()
    time.sleep(3)
    tello.move_forward(pythagorean)
    time.sleep(3)
    tello.rotate_clockwise(180)
    time.sleep(2.5)
    tello.land()

try:
    if state:
        print("Battery Percentage: " + str(tello.get_battery()) + "%")
        if not tookoff:
            tello.takeoff()
            tookoff = True
            tello.send_rc_control(0,0,0,0)
            time.sleep(5)
            print("Lift off has been achieved")
            if state and not wall:
                tello.move_up(70)
                time.sleep(3)
    if state and wall:
        doFirstObstacle(wallHeightInput) 
    time.sleep(1.5)
    
    counter = 0
    while True: 
        distVideo()
        if flag:
            shutOff = True 
            if state:
                tello.send_rc_control(0,0,0,0)
                print("Pythagorean:", pythagorean)
                print("Height Target:", heightTarget)
                if pythagorean >= 200 and counter == 0:
                    counter = 1
                    delta = pythagorean - 200
                    if delta > 20:
                        print("Moving delta", delta, "cm")
                        time.sleep(1.25 + 1.23*Di/1000)
                        tello.move_forward(delta)
                        perfectTime = 100000000000
                        time.sleep(1.25 + 1.23*Di/1000)
                    else: 
                        break
                    flag = False
                    continue
            break

    if state:
        print("Final move command: moving " + str(pythagorean) + " cm")
        time.sleep(1 + Di/1000)
        tello.move_forward(pythagorean)
        time.sleep(3 + 2.33*Di/1000)
        print("Beginning landing")
        tello.rotate_clockwise(180)
        time.sleep(3)
        # print("Total flight time:", tello.get_flight_time(), "seconds", "and", str(tello.get_battery()), "%")
        tello.land()
        time.sleep(3)
        lastMove()


    cv2.destroyAllWindows()
    print("Total flight time:", tello.get_flight_time(), "seconds", "and", str(tello.get_battery()), "%")
except (KeyboardInterrupt, SystemExit, SystemError):
    shutOff = True
    if state:
        time.sleep(0.5)
        print("Total flight time: ", tello.get_flight_time(), " seconds")
        print("Final Battery: ", str(tello.get_battery()), "%")
        tello.send_rc_control(0,0,0,0)
        tello.land()
        #tello.emergency()
        time.sleep(1)
    print('\n!~~~~ Recieved Keyboard Interrupt, quitting thread ~~~~!\n')