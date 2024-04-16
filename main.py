from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator

import time
import cv2
import numpy as np
from mss import mss

## uncomment the bottom two to check if yolov8 is running on cpu or gpu
# import ultralytics
# ultralytics.checks()

#####################
# SETTINGS for button to be pressed
#####################
crouch = 0
jump = 1

#####################
# SETTINGS for game
#####################

# coords, there are 3 possible positions, but assuming that all lanes are equally generated, we only need 1 coord
playerCoords = (250, 330)
actionRange = 100 #the range before a box is considered to be in the action range


#####################
# OTHER SETTINGS
#####################

# debug display
debug = False

# yolov8 model initialization
model = YOLO('infinityrace.pt')

#test screen capture position
mon = {'top': 300, 'left': 500, 'width': 1280, 'height': 720}
sct = mss()

#####################

def press_key(key):
    if key == crouch:
        print("Crouch")
    elif key == jump:
        print("Jump")
    else:
        print("Invalid key")


def determine_action(boxes, nparray):
    #in each box, there is xyxy
    for box in boxes:
        b = box.xyxy[0]  # get box coordinates in (left, top, right, bottom) format
        # the playercoords provided will be the bottom of the player
        # the player stays in the same x position
        # the stone boxes move towards the players x position, incoming from the right to the left
        # the player can jump or crouch to avoid the boxes
        # if the player is within 100 pixels of the box, then perform action

        #there are 2 types of stones, one is [263,308,308,359]
        
        #check if the x position of this box is within 100 pixels of the player, and if the y position of the bottom of the box is within the y position of the player
        if (b[0] >= playerCoords[0] and b[0] <= playerCoords[0] + actionRange) and (b[3] >= playerCoords[1] - actionRange and b[3] <= playerCoords[1] + actionRange):
            #perform action
            #if the box is above the player, then crouch
            if debug:
                cv2.rectangle(nparray, (int(b[0].item()), int(b[1].item())), (int(b[2].item()), int(b[3].item())), (0, 255, 0), 2)
            
            if b[3] < playerCoords[1]:
                #show crouch text
                if debug:
                    cv2.putText(nparray, "Crouch", (playerCoords[0], playerCoords[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                press_key(crouch)
            else:
                #show jump text
                if debug:
                    cv2.putText(nparray, "Jump", (playerCoords[0], playerCoords[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                press_key(jump)
            if debug:
                cv2.imshow('test2', nparray)
            break


####################
# PREDICTION LOOP
####################

# opencv initialization
while True:
    #start time
    start = time.time()
    img = sct.grab(mon)
    nparray = np.array(img)
    # #4 channel to 3 channel
    nparray = cv2.cvtColor(nparray, cv2.COLOR_BGRA2BGR)

    
    # give opencv image to yolov8 model
    results = model(nparray, verbose=False)

    #get the result boxes
    for r in results:

        annotator = Annotator(nparray)
        boxes = r.boxes
        if debug:
            determine_action(boxes, nparray)
        else:
            determine_action(boxes, None)

        #this is for debugging
        for box in boxes:
            b = box.xyxy[0]  # get box coordinates in (left, top, right, bottom) format
            c = box.cls
            annotator.box_label(b, model.names[int(c)])

    nparray = annotator.result()
    #cv2 draw rect on playercoords
    cv2.rectangle(nparray, playerCoords, (playerCoords[0]+10, playerCoords[1]+10), (0, 255, 0), 2)
    #cv2 draw red rect on playercoords + action range
    cv2.rectangle(nparray, (playerCoords[0]+actionRange, playerCoords[1]), (playerCoords[0]+10, playerCoords[1]+10), (0, 0, 255), 2)

    if debug:
        cv2.imshow('test', nparray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break

    #end time
    end = time.time()

    #print time
    # if debug:
    #     print(f"Time taken: {end-start}")
    #60 frames per second, minus the time taken to capture the screen, if not negative
    sleeptime = 1/60 - (end-start)
    
    if sleeptime > 0:
        time.sleep(sleeptime)