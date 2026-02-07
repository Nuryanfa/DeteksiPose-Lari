import cv2
import mediapipe as mp
import time
import math
import numpy as np
from utils import calculate_angle

def draw_graph_overlay(img, data_list, color=(0, 255, 0), max_val=180, title="Angle"):
    """
    Draws a simple line graph overlay on the image.
    data_list: List of numerical values (e.g., angles)
    """
    if not data_list: return img
    
    h, w = img.shape[:2]
    graph_h = 100
    graph_w = 200
    x_start = w - graph_w - 20
    y_start = h - graph_h - 20
    
    # Background
    cv2.rectangle(img, (x_start, y_start), (x_start + graph_w, y_start + graph_h), (0.0, 0, 0, 0.5), cv2.FILLED) # Semi-transparent black if possible, else solid black
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
        """
        Inisialisasi PoseDetector menggunakan MediaPipe Pose.
        Complexity 2 (Heavy) digunakan untuk akurasi lebih tinggi.
        Default Confidence ditingkatkan ke 0.7 agar hasil lebih 'melekat' dan akurat.
        """
        self.mode = mode
        self.complexity = complexity
        self.smooth = smooth
        self.enable_segmentation = enable_segmentation
        self.smooth_segmentation = smooth_segmentation
        self.detection_confidence = detection_confidence
        self.track_confidence = track_confidence

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        
        # Konfigurasi Pose
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
        """
        Mendeteksi pose dan menggambar skeleton kustom dengan Tulang Belakang (Spine).
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(img_rgb)
        
        if self.results.pose_landmarks:
            if draw:
                # Custom Drawing
                self.draw_custom_skeleton(img)
        return img
    
    def draw_custom_skeleton(self, img):
        """
        Menggambar skeleton kustom dengan ukuran konsisten.
        """
        h, w, c = img.shape
        lms = self.results.pose_landmarks.landmark
        
        # Helper untuk mendapatkan koord x,y
        def get_pt(idx):
            return int(lms[idx].x * w), int(lms[idx].y * h)
        
        # Fixed Sizes (Konsisten)
        rad_small = 4
        rad_med = 6
        rad_large = 8
        thick_line = 3
        thick_spine = 4
        
        # --- 1. Gambar Tulang Belakang (Spine) ---
        # Titik tengah bahu (antara 11 dan 12)
        x11_i, y11_i = get_pt(11)
        x12_i, y12_i = get_pt(12)
        center_shoulder = ((x11_i + x12_i) // 2, (y11_i + y12_i) // 2)
        
        # Titik tengah pinggul (antara 23 dan 24)
        x23_i, y23_i = get_pt(23)
        x24_i, y24_i = get_pt(24)
        center_hip = ((x23_i + x24_i) // 2, (y23_i + y24_i) // 2)
        
        # Garis Spine (Kuning)
        cv2.line(img, center_shoulder, center_hip, (0, 255, 255), thick_spine)
        cv2.circle(img, center_shoulder, rad_med, (0, 255, 255), cv2.FILLED)
        cv2.circle(img, center_hip, rad_med, (0, 255, 255), cv2.FILLED)

        # --- 2. Gambar Koneksi Standar dengan Warna Kustom ---
        # KONEKSI (Start Point, End Point, Warna)
        connections = [
            # Tangan Kanan (Merah)
            (12, 14, (0, 0, 255)), (14, 16, (0, 0, 255)),
            # Tangan Kiri (Hijau)
            (11, 13, (0, 255, 0)), (13, 15, (0, 255, 0)),
            # Badan (Putih)
            (11, 12, (200, 200, 200)), (23, 24, (200, 200, 200)),
            (12, 24, (200, 200, 200)), (11, 23, (200, 200, 200)),
            # Kaki Kanan (Merah)
            (24, 26, (0, 0, 255)), (26, 28, (0, 0, 255)), (28, 30, (0, 0, 255)), (28, 32, (0, 0, 255)),
            # Kaki Kiri (Hijau)
            (23, 25, (0, 255, 0)), (25, 27, (0, 255, 0)), (27, 29, (0, 255, 0)), (27, 31, (0, 255, 0))
        ]

        # Draw Lines
        for p1, p2, color in connections:
            if lms[p1].visibility > 0.5 and lms[p2].visibility > 0.5:
                cv2.line(img, get_pt(p1), get_pt(p2), color, thick_line)

        # Draw Circles (Nodes)
        # Kepala
        for idx in range(0, 11):
            if lms[idx].visibility > 0.5:
                cv2.circle(img, get_pt(idx), rad_small, (0, 255, 255), cv2.FILLED)
        
        # Sendi Utama (Termasuk Siku)
        joint_indices = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
        for idx in joint_indices:
            if lms[idx].visibility > 0.5:
                cv2.circle(img, get_pt(idx), rad_med, (255, 255, 255), cv2.FILLED)
                cv2.circle(img, get_pt(idx), rad_large, (0, 0, 0), 2)

    def find_position(self, img, draw=True):
        """
        Mengembalikan daftar koordinat landmark tubuh.
        """
        self.lm_list = []
        if self.results.pose_landmarks:
            h, w, c = img.shape
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lm_list.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.lm_list

    def find_angle(self, img, p1, p2, p3, draw=True):
        """
        Menghitung sudut antara tiga landmark (p1, p2, p3).
        """
        # Pastikan landmark list sudah terisi
        if len(self.lm_list) < max(p1, p2, p3):
            return 0

        # Ambil koordinat
        x1, y1 = self.lm_list[p1][1:]
        x2, y2 = self.lm_list[p2][1:]
        x3, y3 = self.lm_list[p3][1:]

        # Hitung sudut
        angle = calculate_angle((x1, y1), (x2, y2), (x3, y3))

        # Gambar visualisasi
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 2)
            
            cv2.circle(img, (x1, y1), 4, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 4, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x3, y3), 4, (0, 0, 255), cv2.FILLED)
            
            # Text Style
            text = str(int(angle)) + " deg"
            font = cv2.FONT_HERSHEY_PLAIN
            scale = 1.5
            thickness = 2
            (w, h), _ = cv2.getTextSize(text, font, scale, thickness)
            
            # Background rectangle for text
            cv2.rectangle(img, (x2 - 20, y2 + 10), (x2 - 20 + w, y2 + 10 + h + 5), (0, 0, 0), cv2.FILLED)
            cv2.putText(img, text, (x2 - 20, y2 + 30), font, scale, (255, 255, 255), thickness)
        
        return angle
    
    def find_world_pose(self):
        """
        Mengembalikan pose_world_landmarks (Koordinat 3D Real-world dalam meter).
        """
        if self.results.pose_world_landmarks:
            return self.results.pose_world_landmarks.landmark
        return None

class GaitAnalyzer:
    def __init__(self):
        # Metrics
        self.step_count = 0
        self.cadence = 0.0 # steps per minute
        self.stride_length = 0.0 # meters
        self.left_symmetry = 50.0 # % contribution
        self.right_symmetry = 50.0 # % contribution
        self.gct = 0.0 # ms (Ground Contact Time)
        
        # Smooth Angles (LPF)
        self.current_knee_angle = 0
        self.current_hip_angle = 0
        self.alpha = 0.3 # Smoothing factor (0.1 = very smooth/slow, 0.9 = responsive/jittery)
        
        # Internal State
        self.prev_foot_dist = 0
        self.is_increasing = False
        self.last_step_time = time.time()
        
        # Buffers
        self.step_intervals = [] 
        self.left_step_lengths = []
        self.right_step_lengths = []
        
        # GCT Estimation
        self.ground_frames = 0
        self.air_frames = 0
        self.contact_ratio_buffer = []

        # Data Logging
        self.data_log = [] # List of dicts for CSV
        
        # Thresholds
        self.min_step_dist = 0.2 
        self.ground_threshold_y = 0.0

    def update(self, world_lms, fps, raw_knee_angle, raw_hip_angle):
        if not world_lms: return

        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # --- 0. Smoothing Angles (EMA) ---
        if self.current_knee_angle == 0: 
            self.current_knee_angle = raw_knee_angle
            self.current_hip_angle = raw_hip_angle
        else:
            self.current_knee_angle = (self.alpha * raw_knee_angle) + ((1 - self.alpha) * self.current_knee_angle)
            self.current_hip_angle = (self.alpha * raw_hip_angle) + ((1 - self.alpha) * self.current_hip_angle)

        # Store for graphs (Smoothed)
        self.knee_angles_history.append(self.current_knee_angle)
        self.timestamps.append(elapsed)
        if len(self.knee_angles_history) > 300: 
             self.knee_angles_history.pop(0)
             self.timestamps.pop(0)

        # Log Data
        self.data_log.append({
            'timestamp': round(elapsed, 2),
            'knee_angle': int(self.current_knee_angle),
            'hip_angle': int(self.current_hip_angle),
            'cadence': int(self.cadence),
            'stride_length': round(self.stride_length, 2),
            'gct': int(self.gct)
        })

        # Indices: 27=L_Ankle, 28=R_Ankle, 29=L_Heel, 30=R_Heel
        l_ankle = world_lms[27]
        r_ankle = world_lms[28]
        l_heel = world_lms[29]
        r_heel = world_lms[30]
        
        # --- 1. Stride & Cadence (Robust Peak Detection) ---
        dist_x = l_ankle.x - r_ankle.x
        dist_z = l_ankle.z - r_ankle.z
        current_foot_dist = math.sqrt(dist_x**2 + dist_z**2)
        
        # Only check peaks if distance is significant (State Machine)
        if current_foot_dist > self.prev_foot_dist:
            self.is_increasing = True
        elif self.is_increasing and current_foot_dist < self.prev_foot_dist:
            # Peak detected (Extension Max)
            time_since_last = current_time - self.last_step_time
            
            # Robustness 1: Min Distance (0.2m)
            # Robustness 2: Min Time (0.25s -> max 240 SPM, reasonable limit to filter jitter)
            if self.prev_foot_dist > self.min_step_dist and time_since_last > 0.25:
                self.register_step(current_time, self.prev_foot_dist, l_ankle, r_ankle)
            self.is_increasing = False
            
        self.prev_foot_dist = current_foot_dist

        # --- 2. Ground Contact Time (GCT) ---
        lowest_y = max(l_heel.y, r_heel.y)
        if self.ground_threshold_y == 0 or lowest_y > self.ground_threshold_y:
            self.ground_threshold_y = lowest_y
            
        is_grounded = (l_heel.y > self.ground_threshold_y - 0.05) or (r_heel.y > self.ground_threshold_y - 0.05)
        
        if is_grounded: self.ground_frames += 1
        else: self.air_frames += 1
            
        if self.ground_frames + self.air_frames > fps and fps > 0:
            total_f = self.ground_frames + self.air_frames
            ratio = self.ground_frames / total_f
            
            if self.cadence > 0:
                step_duration_s = 60.0 / self.cadence
                # GCT cap (max 1000ms just in case)
                est_gct = ratio * step_duration_s * 1000
                self.gct = est_gct if est_gct < 1000 else self.gct
            
            self.ground_frames = 0
            self.air_frames = 0
            
    def register_step(self, time_now, length, l_ankle, r_ankle):
        self.step_count += 1
        duration = time_now - self.last_step_time
        self.last_step_time = time_now
        
        # Filter realistic duration (0.25s to 2.0s)
        if 0.25 < duration < 2.0:
            self.step_intervals.append(duration)
            if len(self.step_intervals) > 5: self.step_intervals.pop(0) # Smaller window for faster response
            avg_duration = sum(self.step_intervals) / len(self.step_intervals)
            self.cadence = 60.0 / avg_duration if avg_duration > 0 else 0
            
        # Outlier rejection for Stride (Max 2.5m)
        if length < 2.5:
            self.stride_length = length
        
        # Symmetry
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

    def save_csv(self, filename="analysis_data.csv"):
        import csv
        if not self.data_log: return
        
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.data_log[0].keys())
                writer.writeheader()
                writer.writerows(self.data_log)
            print(f"Data saved to {filename}")
        except Exception as e:
            print(f"Error saving CSV: {e}")

class AthleticScorer:
    def __init__(self):
        self.score = 0
        self.feedback = []
        
        # Weights
        self.w_knee = 0.30
        self.w_cadence = 0.25
        self.w_sym = 0.20
        self.w_hip = 0.15
        self.w_consist = 0.10
        
    def calculate_score(self, analyzer):
        # 1. Knee Score 
        # Target: High flexion (smaller angle) during swing. 
        # Let's check the MINIMUM angle in history (max flexion).
        history = analyzer.knee_angles_history
        if not history: return 0
        
        # Recent history min angle
        recent_min_angle = min(history[-30:]) if len(history) >= 30 else min(history)
        
        # Target: < 90 deg (bent) is good. < 60 is elite. > 120 is barely skimming.
        if recent_min_angle <= 60: s_knee = 100
        elif recent_min_angle >= 120: s_knee = 40
        else:
            # Linear map 60->100, 120->40
            s_knee = 100 - (recent_min_angle - 60)
            
        # 2. Cadence Score
        # Target > 180 spm (Running standard). Project prompt asks > 4.5 step/s = 270 spm??
        # Prompt: "Cadence > 4.5 step/s" => 270 SPM.
        # Let's scale: 270 = 100, 150 = 60.
        c = analyzer.cadence
        if c >= 270: s_cadence = 100
        elif c <= 120: s_cadence = 50
        else:
             s_cadence = 50 + ((c - 120)/(270-120)) * 50
             
        # 3. Symmetry Score
        # Diff 0 = 100. Diff 10% = 80. Diff 20 = 60.
        diff = abs(analyzer.left_symmetry - analyzer.right_symmetry)
        s_sym = max(0, 100 - (diff * 2))
        
        # 4. Hip Score
        # Hip Extension/Flexion. We passed ONE hip angle. Usually Extension is key.
        # But we don't know phase. Let's assume Range of Motion is key?
        # Or just checking if hip opens up (180).
        # Prompt says "Sudut pinggul 120-140". 
        h = analyzer.current_hip_angle
        if 120 <= h <= 140: s_hip = 100
        else: s_hip = max(50, 100 - abs(h - 130))

        # 5. Consistency
        s_consist = 80 # Placeholder
        
        # Total
        self.score = (s_knee * self.w_knee) + \
                     (s_cadence * self.w_cadence) + \
                     (s_sym * self.w_sym) + \
                     (s_hip * self.w_hip) + \
                     (s_consist * self.w_consist)
                     
        # Feedback
        self.feedback = []
        if c < 160: self.feedback.append(f"Cadence rendah ({int(c)}). Percepat langkah!")
        if diff > 10: self.feedback.append(f"Asimetri tinggi ({int(diff)}%). Perbaiki keseimbangan.")
        if s_knee < 70: self.feedback.append("Angkat lutut lebih tinggi saat ayunan.")
        if s_hip < 70: self.feedback.append("Perhatikan postur pinggul.")
        
        return int(self.score)
