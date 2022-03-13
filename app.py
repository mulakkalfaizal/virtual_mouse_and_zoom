import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from pynput.mouse import Button, Controller
import time
import osascript
import subprocess
import clipboard

#print(f"1: {clipboard.paste()}")

DETECTOR = HandDetector(detectionCon=0.8)

wCam, hCam = 640, 480
pTime = 0
cTime = 0

cap = cv2.VideoCapture(0)
# cap.set(3, wCam)
# cap.set(4, hCam)

mouse = Controller()
detector = DETECTOR

wScr, hScr = 2880, 1800  # Resolution of my laptop display
frameR = 50
smoothening = 5
plocX, plocY = 0, 0
cloxX, clocY = 0, 0


startDistance = None
scale = 0
cx, cy = 500, 500

image_clicked = False

#print(f"2 : {clipboard.paste()}")
while True:
    success, img = cap.read()
    hands, img = detector.findHands(img, draw=True)

    # img1 = cv2.imread('/Users/mohammadfaizal/Desktop/kerala2.png')
    #
    # img[10:177, 10:333] = img1

    # print(len(hands))
    if len(hands) != 0:
        # print(detector.fingersUp(hands[0]))
        lmlist = hands[0]["lmList"]
        x1, y1 = lmlist[8][0:2]
        x2, y2 = lmlist[12][0:2]

        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

        if detector.fingersUp(hands[0]) == [0, 1, 0, 0, 0]:
            print("Moving mode activated")
            #print(f"3: {clipboard.paste()}")

            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

            # print(f'{x1=} => {x3=}')
            # print(f'{y1=} => {y3=}')

            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # move mouse to right when i move hand right and left when left
            mouse.position = (wScr - clocX, clocY)

            # Draw a cricle on the index finger tip
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)

            plocX, plocY = clocX, clocY

        if detector.fingersUp(hands[0]) == [0, 1, 1, 0, 0]:
            print("Clicking Mode activated")
            #print(f"4: {clipboard.paste()}")

            length, info, img = detector.findDistance(lmlist[8][0:2], lmlist[12][0:2], img)
            # print(length)

            if length < 25:
                print("Clicking ..")
                #print(f"5: {clipboard.paste()}")
                # mouse.click(Button.left, 2)
                #clipboard.copy("")
                mouse.click(Button.left, 1)
                #time.sleep(2)
                osascript.osascript(f'tell application "System Events" to keystroke "c" using {{option down, command down}}')
                time.sleep(1)
                file_path = clipboard.paste()
                print(f"{file_path=}")


                image_clicked = True
                #if file_path.endswith('.PNG'):
    if image_clicked and file_path.endswith('.png' or 'jpeg'):
        img1 = cv2.imread(file_path)

        if len(hands) == 2:
            if detector.fingersUp(hands[0]) == [1, 1, 0, 0, 0] and detector.fingersUp(hands[1]) == [1, 1, 0, 0, 0]:
                print("zoom gesture")
                lmlist1 = hands[0]["lmList"]
                lmlist2 = hands[1]["lmList"]

                # Point 8 is the tip of index finger
                if startDistance is None:
                    length, info, img = detector.findDistance(lmlist1[8][0:2], lmlist2[8][0:2], img)
                    #print(f"{length=}")
                    startDistance = length

                length, info, img = detector.findDistance(lmlist1[8][0:2], lmlist2[8][0:2], img)
                scale = int(length - startDistance) // 2
                cx, cy = info[4:]
                #print(f"{scale=}")
            else:
                startDistance = None

        try:
            h1, w1, _ = img1.shape
            newH, newW = ((h1 + scale) // 2) * 2, ((w1 + scale) // 2) * 2
            img1 = cv2.resize(img1, (newW, newH))

            img[cy - newH // 2:cy + newH // 2, cx - newW // 2:cx + newW // 2] = img1
        # img[10:177, 10:333] = img1
        except:
            pass

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
    cv2.imshow("image", img)
    cv2.waitKey(1)
