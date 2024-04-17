from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator

import time
import cv2
import numpy as np
import win32gui
import win32ui
import win32con
import win32api
import keyboard
from mss import mss

## uncomment the bottom two to check if yolov8 is running on cpu or gpu
# import ultralytics
# ultralytics.checks()

#####################
# SETTINGS for button to be pressed
#####################
crouch = 0x28 # 'down arrow
jump = 'space'

#####################
# SETTINGS for game
#####################
hwnds = []
#default size
w = 2560
h = 1440

# coords, there are 3 possible positions, but assuming that all lanes are equally generated, we only need 1 coord
#potential coords for playerCoords
#2560x1440 = (350, 360) (base size)
#1920x1080 = (260, 270)
#1280x720 = (175, 180)
#1366x768 = (185, 192) (estimated)
playerCoords = (350, 360) 
actionRange = 80 #the range before a box is considered to be in the action range
actionRangeSet2 = 120
actionRangeSet3 = 160 

#####################
# OTHER SETTINGS
#####################

# debug display
debug = True

# yolov8 model initialization
model = YOLO('infinityrace.pt')

#test screen capture position
# mon = {'top': 300, 'left': 500, 'width': 1280, 'height': 720}
# sct = mss()

#####################

#window finder
def winEnumHandler( hwnd, ctx ):
    if win32gui.IsWindowVisible( hwnd ):
        if (win32gui.GetWindowText(hwnd) == "MapleStory"):
            print ( hex( hwnd ), win32gui.GetWindowText( hwnd ) )
            hwnds.append(hwnd)

def press_key(key):
    if key == crouch:
        print("Crouch")
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(0.4)
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
    elif key == jump:
        print("Jump")
        keyboard.press(key)
        time.sleep(0.2)
        keyboard.release(key)
    else:
        print("Invalid key")
    time.sleep(0.1)


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
win32gui.EnumWindows( winEnumHandler, None )
hwnd = hwnds[0]
if (len(hwnds) > 1): #player has chat external
    hwnd = hwnds[1]

#get the correct size
# rect = win32gui.GetWindowRect(hwnd)
# x = rect[0]
# y = rect[1]
# w = rect[2] - x
# h = rect[3] - y

wDC = win32gui.GetWindowDC(hwnd)
dcObj=win32ui.CreateDCFromHandle(wDC)
cDC=dcObj.CreateCompatibleDC()
dataBitMap = win32ui.CreateBitmap()
dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
cDC.SelectObject(dataBitMap)

print(w,h)

# opencv initialization
while True:
    #start time
    start = time.time()
    # img = sct.grab(mon)
    # nparray = np.array(img)
    # Cap Screen
    cDC.BitBlt((0,0),(w, h) , dcObj, (0,0), win32con.SRCCOPY)
    signedIntsArray = dataBitMap.GetBitmapBits(True)

    # #4 channel to 3 channel
    img = np.fromstring(signedIntsArray, dtype='uint8')
    img.shape = (h,w,4)
    nparray = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

    #resize
    nparray = cv2.resize(nparray, (0,0), fx=0.5, fy=0.5) 

    # nparray = cv2.cvtColor(nparray, cv2.COLOR_BGRA2BGR)

    
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
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())
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