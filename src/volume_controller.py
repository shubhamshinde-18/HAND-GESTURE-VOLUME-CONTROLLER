import cv2
import numpy as np
from src.hand_detector import HandDetector
from src.audio.volume_manager import VolumeManager
from src.ui.overlay import UIOverlay
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class VolumeController:
    """Main controller for hand-based volume control"""
    
    def __init__(self, camera_id=0, frame_width=940, frame_height=1080, enable_audio=True):
        self.camera_id = camera_id
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.enable_audio = enable_audio
        
        self.hand_detector = HandDetector()
        self.volume_manager = VolumeManager(enabled=enable_audio)
        self.ui_overlay = UIOverlay(frame_width, frame_height)
        
        self.cap = None
        self._init_camera()
        
        logger.info(f"Volume Controller initialized (Audio: {enable_audio})")
    
    def _init_camera(self):
        """Initialize camera capture"""
        self.cap = cv2.VideoCapture(self.camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera {self.camera_id}")
        
        logger.info(f"Camera {self.camera_id} opened successfully")
    
    def process_frame(self, frame):
        """Process a single frame"""
        
        frame = self.hand_detector.find_hands(frame)
        
        volume_info = {
            'current': self.volume_manager.get_volume(),
            'active': False,
            'finger_distance': 0
        }

        if not self.hand_detector.results or not self.hand_detector.results.multi_hand_landmarks:
            frame = self.ui_overlay.draw_volume_bar(frame, volume_info)
            frame = self.ui_overlay.draw_info_text(frame, volume_info, self.enable_audio)
            return frame
        
        results = self.hand_detector.results
        
        detected_hands = []
        
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            handedness = results.multi_handedness[idx].classification[0].label
            
            h, w, _ = frame.shape
            landmarks = []
            for lm in hand_landmarks.landmark:
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmarks.append([cx, cy])
            
            if len(landmarks) < 9:
                continue 

            detected_hands.append({
                'label': handedness,
                'landmarks': landmarks
            })

            if len(detected_hands) == 2:
                try:
                    left_hand = next((h['landmarks'] for h in detected_hands if h['label'] == 'Left'), None)
                    right_hand = next((h['landmarks'] for h in detected_hands if h['label'] == 'Right'), None)
                    
                    if left_hand and right_hand:
                        left_thumb = left_hand[4]
                        left_index = left_hand[8]
                        right_thumb = right_hand[4]
                        right_index = right_hand[8]
                        
                        distance_left_thumb_right_index = self.hand_detector.calculate_distance(left_thumb, right_index)
                        distance_right_thumb_left_index = self.hand_detector.calculate_distance(right_thumb, left_index)
                        
                        if distance_left_thumb_right_index <= distance_right_thumb_left_index:
                            # Left thumb + Right index
                            distance = distance_left_thumb_right_index
                            point1, point2 = left_thumb, right_index
                        else:
                            # Right thumb + Left index
                            distance = distance_right_thumb_left_index
                            point1, point2 = right_thumb, left_index
                        
                        # Convert distance to volume
                        volume = int(np.clip(np.interp(distance, [20, 200], [0, 100]), 0, 100))
                        self.volume_manager.set_volume(volume)

                        volume_info.update({
                            'active': True,
                            'finger_distance': distance,
                            'current': volume
                        })

                        frame = self.ui_overlay.draw_finger_connection(frame, point1, point2)

                except Exception:
                    pass  

            elif len(detected_hands) == 1:
                try:
                    hand = detected_hands[0]['landmarks']
                    
                    fingers_up = self.hand_detector.count_fingers_up(hand)

                    if fingers_up[1] and fingers_up[2]:
                        thumb_tip = hand[4]
                        index_tip = hand[8]

                        distance = self.hand_detector.calculate_distance(thumb_tip, index_tip)
                        
                        volume = int(np.clip(np.interp(distance, [20, 200], [0, 100]), 0, 100))
                        self.volume_manager.set_volume(volume)

                        volume_info.update({
                            'active': True,
                            'finger_distance': distance,
                            'current': volume
                        })

                        frame = self.ui_overlay.draw_finger_connection(frame, thumb_tip, index_tip)

                except Exception:
                    pass  

            frame = self.ui_overlay.draw_volume_bar(frame, volume_info)
            frame = self.ui_overlay.draw_info_text(frame, volume_info, self.enable_audio)
        return frame

    def run(self):
        """Main run loop"""
        logger.info("Starting main loop (Press 'q' to quit)")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("Failed to read frame from camera")
                    break
                
                frame = cv2.flip(frame, 1)
                
                frame = self.process_frame(frame)
                
                cv2.imshow('Hand Volume Controller', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        logger.info("Resources cleaned up")