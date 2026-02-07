import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import threading
import yt_dlp
import time
import matplotlib.pyplot as plt
from pose_module import PoseDetector, GaitAnalyzer, AthleticScorer, draw_graph_overlay

class PoseApp:
    # ... (existing init and other methods) ...

    def stop_detection(self):
        self.is_running = False
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        
        # Save CSV automatically on stop
        # You might want to access the analyzer instance from the thread, but it's local to run_logic.
        # Ideally, run_logic should handle the saving or expose the analyzer.
        # Let's handle it inside run_logic's cleanup/end block instead.
        
    # ... (other methods) ...

    def run_logic(self, mode, source, complexity):
        # ... (setup code) ...
        
        # Detector Init
        detector = PoseDetector(
            complexity=complexity, 
            detection_confidence=det_conf, 
            track_confidence=track_conf
        )
        gait_analyzer = GaitAnalyzer()
        scorer = AthleticScorer()
        
        def process_and_show(image, fps=30):
            image = self.resize_frame(image)
            image = detector.find_pose(image)
            lm_list = detector.find_position(image)
            
            # ... (Angle calculations) ...
            r_knee_angle = 180
            r_hip_angle = 180
            if len(lm_list) != 0:
                 r_knee_angle = detector.find_angle(image, 24, 26, 28, draw=True)
                 r_hip_angle = detector.find_angle(image, 12, 24, 26, draw=True)
                 detector.find_angle(image, 23, 25, 27, draw=False)
                 detector.find_angle(image, 11, 23, 25, draw=False)

            # Gait Update
            world_lms = detector.find_world_pose()
            if world_lms:
                gait_analyzer.update(world_lms, fps, r_knee_angle, r_hip_angle)
                
                # ... (Existing Text Overlay) ...
                h, w = image.shape[:2]
                overlay_w = 300
                cv2.rectangle(image, (0, 0), (overlay_w, h), (0, 0, 0), cv2.FILLED)
                
                # ... (Text PutCodes) ...
                live_score = scorer.calculate_score(gait_analyzer)
                # (Keep existing text code)
                y_pos = 40
                gap = 35
                c_white = (255, 255, 255)
                c_green = (0, 255, 0)
                c_yellow = (0, 255, 255)
                
                cv2.putText(image, "ATHLETIC METRICS", (10, y_pos), cv2.FONT_HERSHEY_PLAIN, 1.5, c_green, 2)
                y_pos += gap
                cv2.putText(image, f"Score: {live_score}", (10, y_pos), cv2.FONT_HERSHEY_PLAIN, 2, (0, 165, 255), 2)
                y_pos += gap + 10
                cv2.putText(image, f"Cadence: {int(gait_analyzer.cadence)} spm", (10, y_pos), cv2.FONT_HERSHEY_PLAIN, 1.2, c_white, 1)
                y_pos += gap
                cv2.putText(image, f"Stride: {gait_analyzer.stride_length:.2f} m", (10, y_pos), cv2.FONT_HERSHEY_PLAIN, 1.2, c_white, 1)
                y_pos += gap
                cv2.putText(image, f"GCT (Est): {int(gait_analyzer.gct)} ms", (10, y_pos), cv2.FONT_HERSHEY_PLAIN, 1.2, c_yellow, 1)
                y_pos += gap
                cv2.putText(image, f"Sym L/R: {int(gait_analyzer.left_symmetry)}/{int(gait_analyzer.right_symmetry)}%", (10, y_pos), cv2.FONT_HERSHEY_PLAIN, 1.2, c_white, 1)
                y_pos += gap + 10
                cv2.putText(image, "ANGLES (Right)", (10, y_pos), cv2.FONT_HERSHEY_PLAIN, 1.5, c_green, 2)
                y_pos += gap
                cv2.putText(image, f"Knee: {int(r_knee_angle)} deg", (10, y_pos), cv2.FONT_HERSHEY_PLAIN, 1.2, c_white, 1)
                y_pos += gap
                cv2.putText(image, f"Hip : {int(r_hip_angle)} deg", (10, y_pos), cv2.FONT_HERSHEY_PLAIN, 1.2, c_white, 1)

                # --- NEW GRAPH OVERLAY ---
                # Draw Knee Angle Graph at Bottom Right
                image = draw_graph_overlay(image, gait_analyzer.knee_angles_history, color=(0, 255, 255), title="Knee Angle")

            return image

        # ... (Loop Logic) ...
        # (Inside the loop, existing code handles image/video processing)
        
        # Cleanup Block (After loop ends)
        if cap: cap.release()
        cv2.destroyAllWindows()
        self.stop_detection()
        
        # AUTO SAVE CSV
        timestamp_str = time.strftime("%Y%m%d-%H%M%S")
        filename = f"analysis_session_{timestamp_str}.csv"
        gait_analyzer.save_csv(filename)
        
        # Trigger Analysis Report on Main Thread
        self.root.after(0, lambda: self.show_analysis_report(gait_analyzer, scorer))
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Deteksi Postur Tubuh + Gait Analysis (Athletic V2)")
        self.root.geometry("350x650") # Increased height for more controls
        
        # --- Variabel ---
        self.mode = tk.StringVar(value="webcam") # webcam, video, image
        self.source_path = tk.StringVar()
        self.is_running = False
        self.high_accuracy = tk.BooleanVar(value=True) # Default High for Athletic
        self.auto_hide_warnings = tk.BooleanVar(value=True)

        # --- UI Components ---
        self.create_widgets()
        
    def create_widgets(self):
        # Header
        lbl_title = tk.Label(self.root, text="Deteksi Postur Atletik AI", font=("Helvetica", 16, "bold"))
        lbl_title.pack(pady=10)
        
        # Mode Selection
        lbl_mode = tk.Label(self.root, text="Pilih Mode:", font=("Helvetica", 10, "bold"))
        lbl_mode.pack(anchor="w", padx=20)
        
        modes = [
            ("Webcam / DroidCam", "webcam"),
            ("File Video", "video"),
            ("YouTube URL", "youtube"),
            ("File Gambar", "image")
        ]
        
        for text, val in modes:
            rb = tk.Radiobutton(self.root, text=text, variable=self.mode, value=val, command=self.update_ui_state)
            rb.pack(anchor="w", padx=30)
            
        # Input Section
        self.lbl_input = tk.Label(self.root, text="Index Kamera (0, 1):")
        self.lbl_input.pack(pady=(10, 0), anchor="w", padx=20)
        
        self.entry_input = tk.Entry(self.root)
        self.entry_input.pack(fill="x", padx=20)
        self.entry_input.insert(0, "0")
        
        self.btn_browse = tk.Button(self.root, text="Pilih File", command=self.browse_file, state="disabled")
        self.btn_browse.pack(pady=5)
        
        # Settings
        lbl_settings = tk.Label(self.root, text="Pengaturan:", font=("Helvetica", 10, "bold"))
        lbl_settings.pack(anchor="w", padx=20, pady=(15, 0))
        
        chk_accuracy = tk.Checkbutton(self.root, text="High Accuracy (Recommended)", variable=self.high_accuracy)
        chk_accuracy.pack(anchor="w", padx=30)
        
        # Control Buttons
        self.btn_start = tk.Button(self.root, text="MULAI ANALISIS", bg="green", fg="white", font=("Helvetica", 12, "bold"), command=self.start_detection)
        self.btn_start.pack(fill="x", padx=20, pady=20)
        
        self.btn_stop = tk.Button(self.root, text="STOP & LIHAT LAPORAN", bg="red", fg="white", font=("Helvetica", 12, "bold"), command=self.stop_detection, state="disabled")
        self.btn_stop.pack(fill="x", padx=20)
        
        # Info
        lbl_info = tk.Label(self.root, text="Tekan 'q' di jendela video \nuntuk stop manual.", fg="gray")
        lbl_info.pack(pady=10)

    def update_ui_state(self):
        mode = self.mode.get()
        if mode == "webcam":
            self.lbl_input.config(text="Index Kamera / URL DroidCam:")
            self.entry_input.delete(0, tk.END)
            self.entry_input.insert(0, "0")
            self.btn_browse.config(state="disabled")
        elif mode == "video":
            self.lbl_input.config(text="Path Video:")
            self.entry_input.delete(0, tk.END)
            self.btn_browse.config(state="normal")
        elif mode == "image":
            self.lbl_input.config(text="Path Gambar:")
            self.entry_input.delete(0, tk.END)
            self.btn_browse.config(state="normal")
        elif mode == "youtube":
            self.lbl_input.config(text="Link YouTube:")
            self.entry_input.delete(0, tk.END)
            self.btn_browse.config(state="disabled")

    def browse_file(self):
        mode = self.mode.get()
        filetypes = []
        if mode == "video":
            filetypes = [("Video Files", "*.mp4 *.avi *.mov *.mkv")]
        elif mode == "image":
            filetypes = [("Image Files", "*.jpg *.jpeg *.png")]
            
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            self.entry_input.delete(0, tk.END)
            self.entry_input.insert(0, path)

    def get_youtube_stream_url(self, youtube_url):
        ydl_opts = {
            'format': 'best',
            'quiet': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                return info['url']
        except Exception as e:
            messagebox.showerror("Error YouTube", f"Gagal mengambil video: {e}")
            return None

    def start_detection(self):
        mode = self.mode.get()
        source = self.entry_input.get().strip()
        
        if not source and mode != "webcam": 
            if mode == "webcam" and source == "": source = "0"
            else:
                messagebox.showwarning("Peringatan", "Isi input source terlebih dahulu!")
                return

        # Disable buttons
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.is_running = True
        
        # Complexity setting
        complexity = 2 if self.high_accuracy.get() else 1
        
        # Start thread
        t = threading.Thread(target=self.run_logic, args=(mode, source, complexity))
        t.daemon = True
        t.start()

    def stop_detection(self):
        self.is_running = False
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")

    def resize_frame(self, img, max_height=720):
        h, w = img.shape[:2]
        if h > max_height:
            scale = max_height / h
            new_w = int(w * scale)
            new_h = int(h * scale)
            return cv2.resize(img, (new_w, new_h))
        return img
        
    def show_analysis_report(self, analyzer, scorer):
        """Displays Matplotlib graphs and score report"""
        score = scorer.calculate_score(analyzer)
        
        # Create Plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        fig.suptitle(f"Athletic Report - Score: {score}/100", fontsize=16)
        
        # 1. Knee Angle History
        ax1.plot(analyzer.timestamps, analyzer.knee_angles_history, color='blue', label='Knee Angle')
        ax1.axhline(y=90, color='r', linestyle='--', label='Target Max Flexion (<90)')
        ax1.set_title("Knee Flexion Over Time")
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Angle (deg)")
        ax1.legend()
        ax1.grid(True)
        
        # 2. Text Summary
        ax2.axis('off')
        summary_text = f"""
        METRICS SUMMARY:
        ----------------
        • Cadence      : {int(analyzer.cadence)} spm (Target > 180)
        • Stride Len   : {analyzer.stride_length:.2f} m
        • Sym L/R      : {int(analyzer.left_symmetry)}% / {int(analyzer.right_symmetry)}%
        • Est. GCT     : {int(analyzer.gct)} ms
        • Score        : {score} / 100
        
        AI FEEDBACK:
        ------------
        """
        for fb in scorer.feedback:
            summary_text += f"• {fb}\n"
            
        if not scorer.feedback:
            summary_text += "• Teknik lari sangat baik! Pertahankan."
            
        ax2.text(0.1, 0.9, summary_text, fontsize=12, verticalalignment='top', fontfamily='monospace')
        
        plt.tight_layout()
        plt.show()

    def run_logic(self, mode, source, complexity):
        # Prepare CAP
        cap = None
        is_image = False
        
        if mode == "webcam":
            if source.isdigit():
                cap = cv2.VideoCapture(int(source))
            else:
                cap = cv2.VideoCapture(source)
        elif mode == "video":
            cap = cv2.VideoCapture(source)
        elif mode == "youtube":
            print("Mengekstrak URL YouTube...")
            stream_url = self.get_youtube_stream_url(source)
            if not stream_url:
                self.stop_detection()
                return
            cap = cv2.VideoCapture(stream_url)
        elif mode == "image":
            is_image = True
            img = cv2.imread(source)
            if img is None:
                messagebox.showerror("Error", "Gagal membuka gambar.")
                self.stop_detection()
                return
        
        # Detector Init Tuning
        det_conf = 0.5
        track_conf = 0.5
        
        if complexity == 2: # High Accuracy
            det_conf = 0.75
            track_conf = 0.8 # Very sticky tracking
        elif complexity == 1:
            det_conf = 0.6
            track_conf = 0.6
            
        print(f"Starting Detector: Complexity={complexity}, Conf={det_conf}/{track_conf}")
        
        detector = PoseDetector(
            complexity=complexity, 
            detection_confidence=det_conf, 
            track_confidence=track_conf
        )
        gait_analyzer = GaitAnalyzer()
        scorer = AthleticScorer()
        
        def process_and_show(image, fps=30):
            image = self.resize_frame(image)
            image = detector.find_pose(image)
            lm_list = detector.find_position(image)
            
            # Init Angle Vars
            r_knee_angle = 180
            r_hip_angle = 180
            
            # Calculate Angles first to pass to Analyzer
            if len(lm_list) != 0:
                # Need Right Knee: Hip(24)-Knee(26)-Ankle(28)
                r_knee_angle = detector.find_angle(image, 24, 26, 28, draw=True)
                # Need Right Hip: Shoulder(12)-Hip(24)-Knee(26) (Extension)
                r_hip_angle = detector.find_angle(image, 12, 24, 26, draw=True)
                
                # Also draw Left for visual balance
                detector.find_angle(image, 23, 25, 27, draw=False)
                detector.find_angle(image, 11, 23, 25, draw=False)

            # Gait Update
            world_lms = detector.find_world_pose()
            if world_lms:
                gait_analyzer.update(world_lms, fps, r_knee_angle, r_hip_angle)
                
                # --- VISUAL DASHBOARD ---
                # Sidebar Overlay
                h, w = image.shape[:2]
                overlay_w = 300
                cv2.rectangle(image, (0, 0), (overlay_w, h), (0, 0, 0), cv2.FILLED)
                
                # Live Score Calc (simplified)
                live_score = scorer.calculate_score(gait_analyzer)
                
                y_pos = 40
                gap = 35
                
                # Colors
                c_white = (255, 255, 255)
                c_green = (0, 255, 0)
                c_yellow = (0, 255, 255)
                
                cv2.putText(image, "ATHLETIC METRICS", (10, y_pos), cv2.FONT_HERSHEY_PLAIN, 1.5, c_green, 2)
                y_pos += gap
                
                cv2.putText(image, f"Score: {live_score}", (10, y_pos), cv2.FONT_HERSHEY_PLAIN, 2, (0, 165, 255), 2)
                y_pos += gap + 10
                
                cv2.putText(image, f"Cadence: {int(gait_analyzer.cadence)} spm", (10, y_pos), cv2.FONT_HERSHEY_PLAIN, 1.2, c_white, 1)
                y_pos += gap
                
                cv2.putText(image, f"Stride: {gait_analyzer.stride_length:.2f} m", (10, y_pos), cv2.FONT_HERSHEY_PLAIN, 1.2, c_white, 1)
                y_pos += gap
                
                cv2.putText(image, f"GCT (Est): {int(gait_analyzer.gct)} ms", (10, y_pos), cv2.FONT_HERSHEY_PLAIN, 1.2, c_yellow, 1)
                y_pos += gap
                
                cv2.putText(image, f"Sym L/R: {int(gait_analyzer.left_symmetry)}/{int(gait_analyzer.right_symmetry)}%", (10, y_pos), cv2.FONT_HERSHEY_PLAIN, 1.2, c_white, 1)
                y_pos += gap + 10
                
                cv2.putText(image, "ANGLES (Right)", (10, y_pos), cv2.FONT_HERSHEY_PLAIN, 1.5, c_green, 2)
                y_pos += gap
                cv2.putText(image, f"Knee: {int(r_knee_angle)} deg", (10, y_pos), cv2.FONT_HERSHEY_PLAIN, 1.2, c_white, 1)
                y_pos += gap
                cv2.putText(image, f"Hip : {int(r_hip_angle)} deg", (10, y_pos), cv2.FONT_HERSHEY_PLAIN, 1.2, c_white, 1)

            return image

        # --- LOOP ---
        pTime = 0
        
        if is_image:
            img = process_and_show(img, fps=0)
            cv2.imshow("Deteksi AI", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            self.stop_detection()
            # Show Analysis for image?? Maybe less relevant but ok
            self.root.after(0, lambda: self.show_analysis_report(gait_analyzer, scorer))
            return
            
        while self.is_running and cap.isOpened():
            success, img = cap.read()
            if not success:
                print("End of stream.")
                break
            
            cTime = time.time()
            fps = 1 / (cTime - pTime) if (cTime - pTime) != 0 else 0
            pTime = cTime
            
            img = process_and_show(img, fps)
            
            # FPS display (bottom right)
            cv2.putText(img, f'FPS: {int(fps)}', (img.shape[1]-120, img.shape[0]-20), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
            
            cv2.imshow("Deteksi AI", img)
            
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
            if cv2.getWindowProperty("Deteksi AI", cv2.WND_PROP_VISIBLE) < 1:
                break
                
        if cap: cap.release()
        cv2.destroyAllWindows()
        self.stop_detection()
        
        # Trigger Analysis Report on Main Thread
        self.root.after(0, lambda: self.show_analysis_report(gait_analyzer, scorer))

if __name__ == "__main__":
    root = tk.Tk()
    app = PoseApp(root)
    root.mainloop()
