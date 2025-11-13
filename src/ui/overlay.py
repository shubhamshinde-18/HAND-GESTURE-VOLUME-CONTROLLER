import cv2
import numpy as np


class UIOverlay:
    """Draw UI elements on video frames"""
    
    def __init__(self, frame_width, frame_height):
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        self.color_active   = (50, 205, 50)     # Soft Green (active OK state)
        self.color_inactive = (200, 50, 50)     # Soft Red (inactive/waiting)
        self.color_line     = (180, 180, 180)   # Light Grey (neutral UI lines)
        self.color_text     = (230, 230, 230)   # Soft White (clean readable text)
        self.color_bg       = (20, 20, 20)      # Dark Grey Overlay background

    def draw_finger_connection(self, frame, point1, point2, volume_percent=None):
        """Draw premium UI between index & middle fingers"""

        dist = int(np.hypot(point2[0] - point1[0], point2[1] - point1[1]))
        line_thickness = max(3, min(dist // 12, 10))
        glow_thickness = line_thickness + 8

        cv2.line(frame, point1, point2, (120, 120, 120), glow_thickness)

        cv2.line(frame, point1, point2, self.color_line, line_thickness)

        for pt in [point1, point2]:
            cv2.circle(frame, pt, 16, (120, 120, 120), cv2.FILLED)
            cv2.circle(frame, pt, 10, self.color_active, cv2.FILLED)

        center = ((point1[0] + point2[0]) // 2,
                (point1[1] + point2[1]) // 2)
        
        cv2.circle(frame, center, max(6, line_thickness), self.color_active, cv2.FILLED)

        return frame
    
    def draw_volume_bar(self, frame, volume_info):
        """Draw vertical volume bar"""

        bar_x = self.frame_width - 80
        bar_y = 100
        bar_width = 40
        bar_height = 300

        current_volume = volume_info['current']
        is_active = volume_info['active']

        cv2.rectangle(
            frame,
            (bar_x, bar_y),
            (bar_x + bar_width, bar_y + bar_height),
            self.color_inactive,
            2
        )

        fill_height = int((current_volume / 100) * bar_height)
        fill_y = bar_y + bar_height - fill_height

        bar_color = self.color_active if is_active else self.color_inactive
        cv2.rectangle(
            frame,
            (bar_x, fill_y),
            (bar_x + bar_width, bar_y + bar_height),
            bar_color,
            cv2.FILLED
        )

        vol_text = f"{current_volume}%"
        cv2.putText(
            frame,
            vol_text,
            (bar_x - 10, bar_y + bar_height + 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            self.color_text,
            2
        )

        return frame

 
    def draw_info_text(self, frame, volume_info, audio_enabled):
        """Draw futuristic info UI panel"""
        is_active = volume_info['active']
        current_volume = volume_info['current']

        panel_x1, panel_y1 = 10, 10
        panel_x2, panel_y2 = 420, 145
        overlay = frame.copy()
        cv2.rectangle(overlay, (panel_x1, panel_y1), (panel_x2, panel_y2),
                    (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.35, frame, 0.65, 0)

        cv2.rectangle(frame, (panel_x1, panel_y1), (panel_x2, panel_y2),
                    (255, 255, 255), 2, cv2.LINE_AA)

        font = cv2.FONT_HERSHEY_SIMPLEX
        thickness = 1 

        info_lines = [
            ("Gesture Volume Controller", self.color_text),
            ("Thumb +Raise index", self.color_text),
            ("Move fingers to adjust volume", self.color_text),
            (f"Status: {'ACTIVE' if is_active else 'Waiting…'}",
            self.color_active if is_active else (0, 100, 255)),
            (f"Volume: {current_volume}%", self.color_active)
        ]

        if not audio_enabled:
            info_lines.append(("DEMO MODE (No audio control)", (0, 120, 255)))

        y_offset = 38
        for i, (text, color) in enumerate(info_lines):
            cv2.putText(frame, text,
                        (25, y_offset + i * 25),
                        font, 0.6, color, thickness, cv2.LINE_AA)

        cv2.putText(frame, "Press 'q' to quit",
                    (20, self.frame_height - 20),
                    font, 0.5, self.color_text, 1, cv2.LINE_AA)

        return frame
