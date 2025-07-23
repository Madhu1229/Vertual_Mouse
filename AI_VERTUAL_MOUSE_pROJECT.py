# import cv2
# import numpy as np
# import HandTrackingModule as htm
# import time
# import autopy


# wCam, hCam = 640,480
# frameR = 100 #Frame Reduction
# smoothening = 7

# pTime=0
# pLocX, pLocY = 0,0
# cLocX, cLocY = 0,0

# cap = cv2.VideoCapture(0)
# cap.set(3,wCam)
# cap.set(4,hCam)

# detector = htm.HandDetector(maxHands=1)
# wScr, hScr = autopy.screen.size()
# print(wScr,hScr)

# while True:
    
#     #1. Find hand Landmarks
#     success, img = cap.read()
#     img = detector.findHands(img)
#     lmList = detector.findPosition(img)
#     bbox = []
    
#     #2. Get the tip of the index and middle fingers
#     if len(lmList)!=0:
#         x1,y1 = lmList[8][1:]
#         x2,y2 = lmList[12][1:]
        
#         print(x1,y1,x2,y2)
        
    
#     #3. Check which fingers are up
#         fingers = detector.fingersUp(lmList)
#         #print(fingers)
#         cv2.rectangle(img,(frameR,frameR),(wCam-frameR,hCam-frameR),
#                           (255,0,255),2)
        
    
#         #4. Only Index Finger :Moving Mode
#         if fingers[1]==1 and fingers[2] == 0:
        
    
#             #5. Convert coordinates
            
#             x3 = np.interp(x1, (frameR,wCam-frameR),(0,wScr))
#             y3 = np.interp(y1, (frameR,hCam-frameR),(0,hScr))
        
#             #6. Smoothen values
#             cLocX = pLocX + (x3-pLocX)/smoothening
#             cLocY = pLocY + (y3-pLocY)/smoothening
            
#             #7. Move Mouse
#             autopy.mouse.move(wScr- cLocX,cLocY)
#             cv2.circle(img,(x1,y1), 15, (255, 0, 255),cv2.FILLED)
#             pLocX, pLocY = cLocX, cLocY
            
#         #8. Both Index and middle fingers are up :clicking mode
#         if fingers[1]==1 and fingers[2] == 1:
            
#             #9. Find distance between fingers
#             length,img,lineInfo = detector.findDistance(8,12,img,lmList)
#             print(length)
            
#             #10. Click mouse if distance short
#             if length <40:
#                 cv2.circle(img, (lineInfo[4], lineInfo[5]), 
#                            15, (8,255,0), cv2.FILLED)
#                 autopy.mouse.click()
#             else:
#                 cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 0, 255), cv2.FILLED)
            
            
    
    
   
    
#     #11. Frame Rate
#     cTime = time.time()
#     fps = 1/(cTime - pTime)
#     pTime = cTime
#     cv2.putText(img,str(int(fps)),(20,50),
#                 cv2.FONT_HERSHEY_PLAIN,3,(255,0,0),3)
    
#     #12. Display
#     cv2.imshow("Image",img)
#     cv2.waitKey(1)
    
import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy
import pyautogui
import datetime

wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 7

pTime = 0
pLocX, pLocY = 0, 0
cLocX, cLocY = 0, 0
scrollPrevY = 0

gesture_cooldown = 1.5  # seconds cooldown between screenshots
last_gesture_time = 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.HandDetector(maxHands=1)
wScr, hScr = autopy.screen.size()
print(wScr, hScr)

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img)

    if len(lmList) == 0:
        scrollPrevY = 0
        pLocX, pLocY = 0, 0
        cv2.imshow("Image", img)
        cv2.waitKey(1)
        continue

    try:
        x1, y1 = lmList[8][1:]  # Index finger tip
        x2, y2 = lmList[12][1:] # Middle finger tip
        xThumb, yThumb = lmList[4][1:]  # Thumb tip
    except:
        continue

    fingers = detector.fingersUp(lmList)
    cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                  (255, 0, 255), 2)

    current_time = time.time()

    # Take screenshot when ONLY thumb finger is up (cooldown to prevent repeats)
    if fingers == [1, 0, 0, 0, 0]:
        cv2.circle(img, (xThumb, yThumb), 15, (0, 255, 255), cv2.FILLED)  # Yellow circle on thumb
        if current_time - last_gesture_time > gesture_cooldown:
            screenshot = pyautogui.screenshot()
            filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot.save(filename)
            print(f"Screenshot saved as {filename}")
            last_gesture_time = current_time

            # Display screenshot for 2 seconds
            screenshot_img = cv2.imread(filename)
            scale_percent = 50
            width = int(screenshot_img.shape[1] * scale_percent / 100)
            height = int(screenshot_img.shape[0] * scale_percent / 100)
            dim = (width, height)
            resized_img = cv2.resize(screenshot_img, dim, interpolation=cv2.INTER_AREA)
            cv2.imshow("Screenshot", resized_img)
            cv2.waitKey(2000)
            cv2.destroyWindow("Screenshot")

    # Moving mode: Only index finger up (move mouse)
    if fingers[1] == 1 and fingers[2] == 0:
        x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
        y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

        cLocX = pLocX + (x3 - pLocX) / smoothening
        cLocY = pLocY + (y3 - pLocY) / smoothening

        autopy.mouse.move(wScr - cLocX, cLocY)
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)

        pLocX, pLocY = cLocX, cLocY
        scrollPrevY = 0  # reset scroll when moving mouse

    # Scroll mode: Index and middle fingers up
    elif fingers[1] == 1 and fingers[2] == 1:
        if scrollPrevY == 0:
            scrollPrevY = y1

        diffY = scrollPrevY - y1
        scrollThreshold = 15
        scrollAmount = 30

        if diffY > scrollThreshold:
            pyautogui.scroll(scrollAmount)
            cv2.putText(img, "Scroll Up", (50, 100),
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)
            scrollPrevY = y1
        elif diffY < -scrollThreshold:
            pyautogui.scroll(-scrollAmount)
            cv2.putText(img, "Scroll Down", (50, 100),
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)
            scrollPrevY = y1

        length, img, lineInfo = detector.findDistance(8, 12, img, lmList)
        if length < 40:
            cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (8, 255, 0), cv2.FILLED)
            autopy.mouse.click()
        else:
            cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 0, 255), cv2.FILLED)

        pLocX, pLocY = 0, 0  # reset mouse movement during scroll

    else:
        scrollPrevY = 0
        pLocX, pLocY = 0, 0

    # FPS display
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50),
                cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)


