import cv2
import mediapipe as mp
import time
import math
import numpy as np
from .utils import calculate_angle

def draw_graph_overlay(img, data_list, color=(0, 255, 0), max_val=180, title="Angle", offset_y=0):
    """
    Draws a simple line graph overlay on the image.
    data_list: List of numerical values (e.g., angles)
    offset_y: Vertical offset from bottom (for stacking graphs)
    """
    if not data_list: return img
    
    h, w = img.shape[:2]
    graph_h = 100
    graph_w = 200
    x_start = w - graph_w - 20
    y_start = h - graph_h - 20 - offset_y
    
    # Background
    cv2.rectangle(img, (x_start, y_start), (x_start + graph_w, y_start + graph_h), (0.0, 0, 0, 0.5), cv2.FILLED) 
    cv2.putText(img, title, (x_start + 5, y_start + 15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    
    # Needs at least 2 points
    if len(data_list) < 2: return img
    
    # Normalize and Draw
    # Take last N points that fit
    points_to_show = data_list[-50:] 
    if len(points_to_show) < 2: return img
    
    step_x = graph_w / (len(points_to_show) - 1)
    
    prev_pt = None
    for i, val in enumerate(points_to_show):
        x = int(x_start + i * step_x)
        y = int(y_start + graph_h - (val / max_val * graph_h))
        curr_pt = (x, y)
        
        if prev_pt:
            cv2.line(img, prev_pt, curr_pt, color, 2)
        prev_pt = curr_pt
        
    return img

class PoseDetector:
    def __init__(self, mode=False, complexity=2, smooth=True, 
                 enable_segmentation=False, smooth_segmentation=True,
                 detection_confidence=0.7, track_confidence=0.7):
        self.mode = mode
        self.complexity = complexity
        self.smooth = smooth
        self.enable_segmentation = enable_segmentation
        self.smooth_segmentation = smooth_segmentation
        self.detection_confidence = detection_confidence
        self.track_confidence = track_confidence

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        
        self.pose = self.mp_pose.Pose(
            static_image_mode=self.mode,
            model_complexity=self.complexity,
            smooth_landmarks=self.smooth,
            enable_segmentation=self.enable_segmentation,
            smooth_segmentation=self.smooth_segmentation,
            min_detection_confidence=self.detection_confidence,
            min_tracking_confidence=self.track_confidence
        )

    def find_pose(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(img_rgb)
        
        if self.results.pose_landmarks:
            if draw:
                self.draw_custom_skeleton(img)
        return img
    
    def draw_custom_skeleton(self, img):
        h, w, c = img.shape
        lms = self.results.pose_landmarks.landmark
        
        def get_pt(idx):
            return int(lms[idx].x * w), int(lms[idx].y * h)
        
        # Fixed Sizes (Konsisten)
        rad_small = 4
        rad_med = 6
        rad_large = 8
        thick_line = 3
        thick_spine = 4
        
        # --- 1. Gambar Tulang Belakang (Spine) ---
        x11_i, y11_i = get_pt(11)
        x12_i, y12_i = get_pt(12)
        center_shoulder = ((x11_i + x12_i) // 2, (y11_i + y12_i) // 2)
        
        x23_i, y23_i = get_pt(23)
        x24_i, y24_i = get_pt(24)
        center_hip = ((x23_i + x24_i) // 2, (y23_i + y24_i) // 2)
        
        cv2.line(img, center_shoulder, center_hip, (0, 255, 255), thick_spine)
        cv2.circle(img, center_shoulder, rad_med, (0, 255, 255), cv2.FILLED)
        cv2.circle(img, center_hip, rad_med, (0, 255, 255), cv2.FILLED)

        # --- 2. Gambar Koneksi Standar dengan Warna Kustom ---
        connections = [
            (12, 14, (0, 0, 255)), (14, 16, (0, 0, 255)),
            (11, 13, (0, 255, 0)), (13, 15, (0, 255, 0)),
            (11, 12, (200, 200, 200)), (23, 24, (200, 200, 200)),
            (12, 24, (200, 200, 200)), (11, 23, (200, 200, 200)),
            (24, 26, (0, 0, 255)), (26, 28, (0, 0, 255)), (28, 30, (0, 0, 255)), (28, 32, (0, 0, 255)),
            (23, 25, (0, 255, 0)), (25, 27, (0, 255, 0)), (27, 29, (0, 255, 0)), (27, 31, (0, 255, 0))
        ]

        for p1, p2, color in connections:
            if lms[p1].visibility > 0.5 and lms[p2].visibility > 0.5:
                cv2.line(img, get_pt(p1), get_pt(p2), color, thick_line)

        # Draw Circles (Nodes)
        for idx in range(0, 11):
            if lms[idx].visibility > 0.5:
                cv2.circle(img, get_pt(idx), rad_small, (0, 255, 255), cv2.FILLED)
        
        joint_indices = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
        for idx in joint_indices:
            if lms[idx].visibility > 0.5:
                cv2.circle(img, get_pt(idx), rad_med, (255, 255, 255), cv2.FILLED)
                cv2.circle(img, get_pt(idx), rad_large, (0, 0, 0), 2)

    def find_position(self, img, draw=True):
        self.lm_list = []
        if self.results.pose_landmarks:
            h, w, c = img.shape
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lm_list.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        # Graphs are now handled by frontend. Disabling in-video drawing to keep feed clean.
        # cv2.rectangle(img, (w - 300, h - 300), (w, h), (0, 0, 0), cv2.FILLED)
        # self.draw_graph(img, self.knee_angles_history, (w - 300, h - 150), (300, 150), (0, 255, 0), "R. Knee")
        # self.draw_graph(img, self.hip_angles_history, (w - 300, h - 300), (300, 150), (255, 0, 0), "R. Hip")
        return self.lm_list

    def find_angle(self, img, p1, p2, p3, draw=True):
        if len(self.lm_list) < max(p1, p2, p3):
            return 0

        x1, y1 = self.lm_list[p1][1:]
        x2, y2 = self.lm_list[p2][1:]
        x3, y3 = self.lm_list[p3][1:]

        angle = calculate_angle((x1, y1), (x2, y2), (x3, y3))

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 2)
            cv2.circle(img, (x1, y1), 4, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 4, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x3, y3), 4, (0, 0, 255), cv2.FILLED)
            
            text = str(int(angle)) + " deg"
            font = cv2.FONT_HERSHEY_PLAIN
            (w, h), _ = cv2.getTextSize(text, font, 1.5, 2)
            cv2.rectangle(img, (x2 - 20, y2 + 10), (x2 - 20 + w, y2 + 10 + h + 5), (0, 0, 0), cv2.FILLED)
            cv2.putText(img, text, (x2 - 20, y2 + 30), font, 1.5, (255, 255, 255), 2)
        
        return angle
    
    def find_world_pose(self):
        if self.results.pose_world_landmarks:
            return self.results.pose_world_landmarks.landmark
        return None

class GaitAnalyzer:
    def __init__(self):
        self.step_count = 0
        self.cadence = 0.0
        self.stride_length = 0.0
        self.left_symmetry = 50.0
        self.right_symmetry = 50.0
        self.gct = 0.0
        self.current_knee_angle = 0
        self.current_hip_angle = 0
        self.swing_mechanics_error = 0
        self.swing_mechanics_error = 0 # Duplicate line in original, preserved or removed? cleaned up implicitly
        self.hip_stability_error = 0
        self.current_arm_angle = 0
        self.current_trunk_angle = 0
        self.alpha = 0.3
        self.prev_foot_dist = 0
        self.is_increasing = False
        self.last_step_time = time.time()
        self.start_time = time.time()
        self.step_intervals = [] 
        self.left_step_lengths = []
        self.right_step_lengths = []
        self.ground_frames = 0
        self.air_frames = 0
        self.data_log = []
        self.min_step_dist = 0.2 
        self.ground_threshold_y = 0.0
        self.knee_angles_history = []
        self.hip_angles_history = []
        self.timestamps = []
        self.current_world_landmarks = []
        self.min_dist_in_cycle = 10.0 # Track closest approach
        self.pass_threshold = 0.15 # Feet must pass closer than 15cm
        
        # New GCT Logic
        self.is_currently_grounded = False
        self.ground_contact_start = 0.0

    def update(self, world_lms, fps, raw_knee_angle, raw_hip_angle, arm_angle=0, trunk_angle=0):
        if not world_lms: return
        self.current_world_landmarks = world_lms

        current_time = time.time()
        elapsed = current_time - self.start_time
        
        if self.current_knee_angle == 0: 
            self.current_knee_angle = raw_knee_angle # Right Knee (Legacy)
            self.l_knee_angle = 0
            self.current_hip_angle = raw_hip_angle # Right Hip (Legacy)
            self.l_hip_angle = 0
            self.current_arm_angle = arm_angle
            self.current_trunk_angle = trunk_angle
        else:
            self.current_knee_angle = (self.alpha * raw_knee_angle) + ((1 - self.alpha) * self.current_knee_angle)
            self.current_hip_angle = (self.alpha * raw_hip_angle) + ((1 - self.alpha) * self.current_hip_angle)
            self.current_arm_angle = (self.alpha * arm_angle) + ((1 - self.alpha) * self.current_arm_angle)
            self.current_trunk_angle = (self.alpha * trunk_angle) + ((1 - self.alpha) * self.current_trunk_angle)
            pass

        # Calculate Error Metrics (Simple Heuristic for MVP)
        if self.current_knee_angle > 140: # Leg too straight
            self.swing_mechanics_error = min(100, (self.current_knee_angle - 140) * 2)
        else:
            self.swing_mechanics_error = max(0, self.swing_mechanics_error - 5)

        # Hip Stability: Hip angle variance.
        hip_dev = abs(180 - self.current_hip_angle)
        if hip_dev > 10:
            self.hip_stability_error = min(100, (hip_dev - 10) * 5)
        else:
             self.hip_stability_error = max(0, self.hip_stability_error - 2)

        # Store for graphs (Smoothed)
        self.knee_angles_history.append(self.current_knee_angle)
        if not hasattr(self, 'hip_angles_history'): self.hip_angles_history = []
        self.hip_angles_history.append(self.current_hip_angle)
        
        if not hasattr(self, 'arm_angles_history'): self.arm_angles_history = []
        self.arm_angles_history.append(self.current_arm_angle)

        if not hasattr(self, 'trunk_angles_history'): self.trunk_angles_history = []
        self.trunk_angles_history.append(self.current_trunk_angle)

        self.timestamps.append(elapsed)
        if len(self.knee_angles_history) > 300: 
             self.knee_angles_history.pop(0)
             if self.hip_angles_history: self.hip_angles_history.pop(0)
             if self.arm_angles_history: self.arm_angles_history.pop(0)
             if self.trunk_angles_history: self.trunk_angles_history.pop(0)
             self.timestamps.pop(0)

        l_ankle = world_lms[27]
        r_ankle = world_lms[28]
        l_heel = world_lms[29]
        r_heel = world_lms[30]
        
        dist_x = l_ankle.x - r_ankle.x
        dist_z = l_ankle.z - r_ankle.z
        current_foot_dist = math.sqrt(dist_x**2 + dist_z**2)
        
        # Track minimum distance in current cycle
        self.min_dist_in_cycle = min(self.min_dist_in_cycle, current_foot_dist)
        
        if current_foot_dist > self.prev_foot_dist:
            self.is_increasing = True
        elif self.is_increasing and current_foot_dist < self.prev_foot_dist:
            time_since_last = current_time - self.last_step_time
            # Validate Step: Must be large enough pulse (>min_step_dist) AND feet must have crossed (<pass_threshold)
            if self.prev_foot_dist > self.min_step_dist and time_since_last > 0.25 and self.min_dist_in_cycle < self.pass_threshold:
                self.register_step(current_time, self.prev_foot_dist, l_ankle, r_ankle)
            self.is_increasing = False
            
        self.prev_foot_dist = current_foot_dist

        lowest_y = max(l_heel.y, r_heel.y)
        if self.ground_threshold_y == 0 or lowest_y > self.ground_threshold_y:
            self.ground_threshold_y = lowest_y
            
        is_grounded = (l_heel.y > self.ground_threshold_y - 0.05) or (r_heel.y > self.ground_threshold_y - 0.05)
        
        if is_grounded: 
            if not self.is_currently_grounded:
                # Started touching ground
                self.ground_contact_start = current_time
                self.is_currently_grounded = True
        else:
            if self.is_currently_grounded:
                # Just left ground (Toe-off)
                contact_time = (current_time - self.ground_contact_start) * 1000 # ms
                # Filter noise (too short contacts likely detection jitter)
                if contact_time > 20: 
                    if self.gct == 0:
                        self.gct = contact_time
                    else:
                        self.gct = (0.2 * contact_time) + (0.8 * self.gct) # Smooth updates
                self.is_currently_grounded = False
            
    def register_step(self, time_now, length, l_ankle, r_ankle):
        self.step_count += 1
        self.min_dist_in_cycle = 10.0 # Reset cycle tracker
        duration = time_now - self.last_step_time
        self.last_step_time = time_now
        
        if 0.25 < duration < 2.0:
            self.step_intervals.append(duration)
            if len(self.step_intervals) > 5: self.step_intervals.pop(0)
            avg_duration = sum(self.step_intervals) / len(self.step_intervals)
            self.cadence = 60.0 / avg_duration if avg_duration > 0 else 0
            
        if length < 2.5:
            self.stride_length = length
        
        if l_ankle.z < r_ankle.z: 
             self.left_step_lengths.append(length)
        else:
             self.right_step_lengths.append(length)
             
        if len(self.left_step_lengths) > 10: self.left_step_lengths.pop(0)
        if len(self.right_step_lengths) > 10: self.right_step_lengths.pop(0)
        
        avg_l = sum(self.left_step_lengths) / len(self.left_step_lengths) if self.left_step_lengths else 0
        avg_r = sum(self.right_step_lengths) / len(self.right_step_lengths) if self.right_step_lengths else 0
        total = avg_l + avg_r
        if total > 0:
            self.left_symmetry = (avg_l / total) * 100
            self.right_symmetry = (avg_r / total) * 100

    def get_graph_data(self):
        # Return last 50 points formatted for chart.js
        # We need to ensure lists are same length
        min_len = min(len(self.timestamps), len(self.knee_angles_history))
        if hasattr(self, 'hip_angles_history'):
             min_len = min(min_len, len(self.hip_angles_history))
        
        # Take last 50
        start_idx = max(0, min_len - 50)
        
        return {
            "labels": [f"{t:.1f}s" for t in self.timestamps[start_idx:min_len]],
            "knee": self.knee_angles_history[start_idx:min_len],
            "hip": self.hip_angles_history[start_idx:min_len] if hasattr(self, 'hip_angles_history') else []
        }

    def save_csv(self, filename):
        import csv
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'RightKneeAngle', 'RightHipAngle', 'Cadence', 'StrideLength'])
            
            # Align lists
            min_len = min(len(self.timestamps), len(self.knee_angles_history))
            if hasattr(self, 'hip_angles_history'):
                min_len = min(min_len, len(self.hip_angles_history))
            
            for i in range(min_len):
                row = [
                    f"{self.timestamps[i]:.2f}",
                    f"{self.knee_angles_history[i]:.1f}",
                    f"{self.hip_angles_history[i]:.1f}" if hasattr(self, 'hip_angles_history') and i < len(self.hip_angles_history) else "0",
                    f"{self.cadence:.1f}",
                    f"{self.stride_length:.2f}"
                ]
                writer.writerow(row)

class AthleticScorer:
    def __init__(self):
        self.score = 0
        self.feedback = []
        self.w_knee = 0.30
        self.w_cadence = 0.25
        self.w_sym = 0.20
        self.w_hip = 0.15
        self.w_consist = 0.10
        
    def calculate_score(self, analyzer):
        history = analyzer.knee_angles_history
        if not history: return 0
        
        recent_min_angle = min(history[-30:]) if len(history) >= 30 else min(history)
        
        if recent_min_angle <= 60: s_knee = 100
        elif recent_min_angle >= 120: s_knee = 40
        else:
            s_knee = 100 - (recent_min_angle - 60)
            
        c = analyzer.cadence
        if c >= 270: s_cadence = 100
        elif c <= 120: s_cadence = 50
        else:
             s_cadence = 50 + ((c - 120)/(270-120)) * 50
             
        diff = abs(analyzer.left_symmetry - analyzer.right_symmetry)
        s_sym = max(0, 100 - (diff * 2))
        
        h = analyzer.current_hip_angle
        if 120 <= h <= 140: s_hip = 100
        else: s_hip = max(50, 100 - abs(h - 130))

        s_consist = 80
        
        self.score = (s_knee * self.w_knee) + \
                     (s_cadence * self.w_cadence) + \
                     (s_sym * self.w_sym) + \
                     (s_hip * self.w_hip) + \
                     (s_consist * self.w_consist)
                     
        self.feedback = []
        if c < 160: self.feedback.append(f"Cadence rendah ({int(c)}). Percepat langkah!")
        if diff > 10: self.feedback.append(f"Asimetri tinggi ({int(diff)}%). Perbaiki keseimbangan.")
        if s_knee < 70: self.feedback.append("Angkat lutut lebih tinggi saat ayunan.")
        if s_hip < 70: self.feedback.append("Perhatikan postur pinggul.")
        
        return int(self.score)
