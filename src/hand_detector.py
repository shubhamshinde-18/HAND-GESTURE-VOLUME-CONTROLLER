import cv2
import mediapipe as mp
import math
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class HandDetector:
    """Hand detection and tracking using MediaPipe"""
    
    def __init__(self, max_hands=2, detection_confidence=0.7, tracking_confidence=0.7):
        self.max_hands = max_hands
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence
        
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        
        logger.info("Hand detector initialized")
    
    def find_hands(self, frame, draw=True):
        """Detect hands in frame and optionally draw landmarks"""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(frame_rgb)
        
        if draw and self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
        
        return frame
    
    def get_two_hands_landmarks(self, frame):
        """Return landmarks for Left and Right hand separately if both detected"""
        if not self.results.multi_hand_landmarks or len(self.results.multi_hand_landmarks) < 2:
            return None, None

        left, right = None, None
        h, w, _ = frame.shape

        for idx, hand_handedness in enumerate(self.results.multi_handedness):
            label = hand_handedness.classification[0].label 
            hand_landmarks = self.results.multi_hand_landmarks[idx]

            landmarks = []
            for lm in hand_landmarks.landmark:
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmarks.append((cx, cy))

            if label == 'Left':
                left = landmarks
            else:
                right = landmarks

        return left, right

    def get_landmarks(self, frame):
        """Get hand landmark positions"""
        if not self.results.multi_hand_landmarks:
            return None
        
        hand_landmarks = self.results.multi_hand_landmarks[0]
        h, w, c = frame.shape
        
        landmarks = []
        for lm in hand_landmarks.landmark:
            cx, cy = int(lm.x * w), int(lm.y * h)
            landmarks.append((cx, cy))
        
        return landmarks
    
    def count_fingers_up(self, landmarks):
        """Count which fingers are up (thumb, index, middle, ring, pinky)"""
        if not landmarks or len(landmarks) < 21:
            return [False] * 5
        
        fingers = []
        
        if landmarks[4][0] > landmarks[3][0]:
            fingers.append(True)
        else:
            fingers.append(False)
        
        tip_ids = [8, 12, 16, 20]
        for tip_id in tip_ids:
            if landmarks[tip_id][1] < landmarks[tip_id - 2][1]:
                fingers.append(True)
            else:
                fingers.append(False)
        
        return fingers
    
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        x1, y1 = point1
        x2, y2 = point2
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return distance
    
    def get_finger_position(self, landmarks, finger_id):
        """Get specific finger tip position"""
        if not landmarks or len(landmarks) < finger_id:
            return None
        return landmarks[finger_id]