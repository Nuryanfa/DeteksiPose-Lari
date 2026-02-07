import cv2
import time
from fastapi import APIRouter, Response, HTTPException, Query
from fastapi.responses import StreamingResponse, FileResponse
from app.services.pose_module import PoseDetector, GaitAnalyzer, AthleticScorer, draw_graph_overlay
from app.services.feedback import get_feedback
import yt_dlp
import os
import platform

router = APIRouter()

# Global State
cap = None
analyzer = GaitAnalyzer()
scorer = AthleticScorer()
current_source = 0
is_streaming = False
is_paused = False

# Ensure Upload Dir Exists
UPLOAD_DIR = os.path.abspath("static/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_youtube_stream_url(youtube_url):
    ydl_opts = {
        'format': 'best[height<=480][ext=mp4]/best[height<=480]',
        'quiet': True,
        'noplaylist': True,
        'force_ipv4': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}}, # Try Android for progressive MP4
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            return info['url']
    except Exception as e:
        print(f"Error fetching YouTube URL: {e}")
        return None

def generate_frames():
    global cap, analyzer, scorer, is_streaming, is_paused
    
    detector = PoseDetector(complexity=1) 
    pTime = 0
    
    while is_streaming:
        if is_paused:
            time.sleep(0.1)
            continue
            
        if cap is None or not cap.isOpened():
            break

        try:
            success, frame = cap.read()
        except cv2.error as e:
            print(f"OpenCV Error: {e}")
            break
            
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame = cv2.resize(frame, (800, 600))
        
        # 1. Detection
        frame = detector.find_pose(frame)
        lm_list = detector.find_position(frame, draw=False)
        world_lms = detector.find_world_pose()
        
        # 2. Angle Calc
        r_knee = 180
        r_hip = 180
        if len(lm_list) != 0:
            r_knee = detector.find_angle(frame, 24, 26, 28, draw=True)
            r_hip = detector.find_angle(frame, 12, 24, 26, draw=True)
            detector.find_angle(frame, 23, 25, 27, draw=False) 

        # 3. Analytics Update
        cTime = time.time()
        fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
        pTime = cTime
        
        if world_lms:
            # 3. Calculate Biomechanics
            # A. Arm Swing (Right: Shoulder 12, Elbow 14, Wrist 16)
            # We need pixel coords for 2D angle (visual) or world coords for 3D. 
            # Using 2D (lm_list) is consistent with knee calculation method in pose_module.
            # But here we need to extract from lm_list.
            # lm_list structure: [id, x, y]
            
            # Helper to find point by ID
            def get_p(id):
                for lm in lm_list:
                    if lm[0] == id: return (lm[1], lm[2])
                return None

            r_shoulder = get_p(12)
            r_elbow = get_p(14)
            r_wrist = get_p(16)
            
            r_arm_angle = 0
            if r_shoulder and r_elbow and r_wrist:
                from app.services.utils import calculate_angle
                r_arm_angle = calculate_angle(r_shoulder, r_elbow, r_wrist)

            # B. Trunk Lean (Vertical, Hip 24, Shoulder 12)
            # Create a vertical reference point above the hip
            r_hip_pt = get_p(24)
            r_shoulder_pt = get_p(12)
            
            trunk_angle = 0
            if r_hip_pt and r_shoulder_pt:
                 # Vertical point: same X as hip, but Y is higher (smaller value)
                 vertical_pt = (r_hip_pt[0], r_hip_pt[1] - 100)
                 from app.services.utils import calculate_angle
                 trunk_angle = calculate_angle(vertical_pt, r_hip_pt, r_shoulder_pt)

            analyzer.update(world_lms, fps, r_knee, r_hip, arm_angle=r_arm_angle, trunk_angle=trunk_angle)
            
        # 4. Draw Overlays (Enhanced with Multiple Graphs)
        # We can draw two graphs side-by-side or stacked
        if analyzer.knee_angles_history:
            # Knee Graph (Green)
            frame = draw_graph_overlay(frame, analyzer.knee_angles_history, color=(0, 255, 0), title="R. Knee", max_val=180, offset_y=0)
            
        if hasattr(analyzer, 'hip_angles_history') and analyzer.hip_angles_history:
            # Hip Graph (Blue) - Stacked below Knee Graph
            frame = draw_graph_overlay(frame, analyzer.hip_angles_history, color=(255, 0, 0), title="R. Hip", max_val=180, offset_y=130)

        # Stats Overlay
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
        cv2.putText(frame, f"Steps: {analyzer.step_count}", (10, 60), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@router.get("/video_feed")
def video_feed(source: str = Query("0")):
    global cap, current_source, is_streaming, analyzer, is_paused
    
    new_source = source
    if source.isdigit():
        new_source = int(source)
    
    try:
        new_source_int = int(source)
        new_source = new_source_int
        # If integer, it's a camera index.
    except ValueError:
        pass # It's a string (URL or path)

    if cap is None or not cap.isOpened() or current_source != new_source:
        if cap: cap.release()
        
        if isinstance(new_source, str) and ("youtube.com" in new_source or "youtu.be" in new_source):
             print(f"Processing YouTube: {new_source}")
             stream_url = get_youtube_stream_url(new_source)
             if stream_url:
                 cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
             else:
                 # Fallback/Error
                 pass
        else:
            # File path or Camera Index
            if isinstance(new_source, int) and platform.system() == 'Windows':
                # Windows requires CAP_DSHOW for some cameras (DroidCam, Iriun)
                cap = cv2.VideoCapture(new_source, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(new_source)
            
        current_source = new_source
        analyzer = GaitAnalyzer() 
    
    is_streaming = True
    is_paused = False
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.post("/stop")
def stop_stream():
    global is_streaming, cap
    is_streaming = False
    if cap:cap.release()
    return {"message": "Stream stopped"}

@router.post("/pause")
def pause_stream():
    global is_paused
    is_paused = True
    return {"message": "Stream paused"}

@router.post("/resume")
def resume_stream():
    global is_paused
    is_paused = False
    return {"message": "Stream resumed"}

@router.post("/restart")
def restart_stream():
    global analyzer, is_paused, cap
    analyzer = GaitAnalyzer()
    is_paused = False
    if cap and cap.isOpened():
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    return {"message": "Stream restarted"}

@router.get("/stats")
def get_stats():
    global analyzer, scorer
    score = scorer.calculate_score(analyzer)
    
    # Determine GCT Status
    gct_val = int(analyzer.gct)
    if gct_val > 0:
        if gct_val < 200: gct_status = "green"
        elif gct_val < 250: gct_status = "yellow"
        else: gct_status = "red"
    else:
        gct_status = "gray"

    return {
        "score": score,
        "duration_seconds": time.time() - analyzer.start_time if analyzer.start_time else 0,
        "cadence": int(analyzer.cadence),
        "step_count": int(analyzer.step_count),
        "stride_length": round(analyzer.stride_length, 2),
        "gct": gct_val,
        "gct_status": gct_status,
        "symmetry": {
            "left": int(analyzer.left_symmetry),
            "right": int(analyzer.right_symmetry)
        },
        "errors": {
            "swing_mechanics": int(analyzer.swing_mechanics_error),
            "hip_stability": int(analyzer.hip_stability_error)
        },
        "biomechanics": {
            "arm_angle": int(analyzer.current_arm_angle),
            "trunk_angle": int(analyzer.current_trunk_angle),
            "world_landmarks": [
                {"x": lm.x, "y": lm.y, "z": lm.z, "visibility": lm.visibility} 
                for lm in analyzer.current_world_landmarks
            ] if analyzer.current_world_landmarks else []
        },
        "graph_data": analyzer.get_graph_data(),
        "feedback": get_feedback({
            "cadence": int(analyzer.cadence),
            "biomechanics": {
                "arm_angle": int(analyzer.current_arm_angle),
                "trunk_angle": int(analyzer.current_trunk_angle)
            },
            "errors": {
                "hip_stability": int(analyzer.hip_stability_error)
            }
        })
    }

@router.post("/export_csv")
def export_csv():
    global analyzer
    filename = os.path.join(UPLOAD_DIR, "analysis_latest.csv")
    try:
        analyzer.save_csv(filename)
        # Using FileResponse to safeguard file access
        return {"download_url": "/static/uploads/analysis_latest.csv"}
    except Exception as e:
        print(f"Export Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
