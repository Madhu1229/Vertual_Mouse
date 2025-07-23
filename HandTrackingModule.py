import cv2
import mediapipe as mp
import math

class HandDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.mode,
                                        max_num_hands=self.maxHands,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.results = None

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        if self.results and self.results.multi_hand_landmarks:
            hand = self.results.multi_hand_landmarks[handNo]

            for id, lm in enumerate(hand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append((id, cx, cy))

                if draw:
                    cv2.circle(img, (cx, cy), 7, (255, 0, 0), cv2.FILLED)

        return lmList

    def fingersUp(self, lmList):
        fingers = []

        if len(lmList) == 0:
            return []

        # Thumb (right hand)
        if lmList[4][1] > lmList[3][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Fingers: Index, Middle, Ring, Pinky
        tips = [8, 12, 16, 20]
        for tip in tips:
            if lmList[tip][2] < lmList[tip - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers
    
    def findDistance(self, p1, p2, img=None, lmList=None):
        """
        Finds distance between two landmarks.
        p1, p2: landmark indexes (like 8 and 12)
        lmList: list of landmarks (from findPosition)
        img: optional image to draw on
        Returns: distance, image, [x1, y1, x2, y2, centerX, centerY]
        """
        if lmList is None or len(lmList) <= max(p1, p2):
            return 0, img, [0, 0, 0, 0, 0, 0]

        x1, y1 = lmList[p1][1], lmList[p1][2]
        x2, y2 = lmList[p2][1], lmList[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        length = math.hypot(x2 - x1, y2 - y1)

        if img is not None:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
            cv2.circle(img, (x1, y1), 7, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 7, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), 7, (0, 255, 0), cv2.FILLED)

        return length, img, [x1, y1, x2, y2, cx, cy]
