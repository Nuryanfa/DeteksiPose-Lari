from flask import Flask, render_template, Response, jsonify, request
import cv2
import os
import time
import yt_dlp
import numpy as np
from pose_module import PoseDetector, GaitAnalyzer, AthleticScorer

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variables for state
video_source = 0  # Default to webcam
current_mode = 'video' # video, image, youtube
static_image_path = None
cap = None
detector = None # Will be initialized dynamically
analyzer = GaitAnalyzer()
scorer = AthleticScorer()

# Control States
is_paused = False
playback_speed = 1.0
current_complexity = 2 # Default High complexity for athletic

def init_detector(mode='video'):
    global detector, current_complexity
    static_mode = (mode == 'image')
    
    # Tuning Config based on Complexity for Athletic Movement
    det_conf = 0.5
    track_conf = 0.5
    
    if current_complexity == 2: # High (Heavy)
        det_conf = 0.75 # Stricter detection
        track_conf = 0.75 # Much stricter tracking for accuracy
    elif current_complexity == 1: # Balanced
        det_conf = 0.6
        track_conf = 0.6
    else: # Fast (Lite)
        det_conf = 0.5
        track_conf = 0.5
        
    print(f"Re-Initializing Detector: Mode={mode}, Complexity={current_complexity}, Conf={det_conf}/{track_conf}")
    
    # Force generic initialization to clear previous state if needed
    detector = PoseDetector(
        mode=static_mode, 
        complexity=current_complexity,
        smooth=not static_mode,
        detection_confidence=det_conf,
        track_confidence=track_conf
    )

@app.route('/set_accuracy', methods=['POST'])
def set_accuracy():
    global current_complexity, current_mode
    data = request.json
    try:
        complexity = int(data.get('complexity', 1))
        current_complexity = complexity 
        print(f"Set Accuracy Request: {complexity}")
        
        # Re-init current mode to apply immediately
        # Determining mode based on current_mode string
        target_mode = 'image' if current_mode == 'image' else 'video'
        init_detector(target_mode)
        
        return jsonify({'success': True, 'message': f'Complexity set to {complexity}'})
    except Exception as e:
        print(f"Error setting accuracy: {e}")
        return jsonify({'error': str(e)}), 500
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'socket_timeout': 10
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Check if it's a valid URL first? extract_info validates it.
            info = ydl.extract_info(youtube_url, download=False)
            return info['url']
    except Exception as e:
        print(f"Error extracting YouTube URL: {e}")
        return None

def generate_frames():
    global cap, video_source, analyzer, scorer, current_mode, static_image_path, is_paused, detector
    
    if detector is None:
        init_detector('video')

    if current_mode == 'video' or current_mode == 'youtube':
        if cap is None or not cap.isOpened():
             cap = cv2.VideoCapture(video_source)
    
    last_frame = None
    
    while True:
        if current_mode == 'image':
            if static_image_path and os.path.exists(static_image_path):
                img = cv2.imread(static_image_path)
                if img is None: continue
                
                # Resize
                width = 1280
                height = int(img.shape[0] * (1280 / img.shape[1]))
                img = cv2.resize(img, (width, height))
                
                # Process
                img = detector.find_pose(img)
                lm_list = detector.find_position(img, draw=False)
                
                # Angles check
                if len(lm_list) != 0:
                     detector.find_angle(img, 24, 26, 28) # Right Knee
                     detector.find_angle(img, 12, 24, 26) # Right Hip
                
                ret, buffer = cv2.imencode('.jpg', img)
                frame = buffer.tobytes()
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                time.sleep(0.5) 
            else:
                time.sleep(0.5)
                continue

        else: # Video or YouTube
            if is_paused and last_frame is not None:
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + last_frame + b'\r\n')
                time.sleep(0.1)
                continue
                
            if cap is None or not cap.isOpened():
                 time.sleep(0.1)
                 continue
                 
            success, frame = cap.read()
            if not success:
                if isinstance(video_source, str) and current_mode == 'video':
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                elif current_mode == 'youtube':
                    cap.release()
                    cap = cv2.VideoCapture(video_source)
                    continue
                else: 
                     continue
            else:
                # Resize
                width = 800 # Reduced for web performance if needed, or keep 1280
                if frame.shape[1] > 0:
                   height = int(frame.shape[0] * (width / frame.shape[1]))
                   frame = cv2.resize(frame, (width, height))

                frame = detector.find_pose(frame)
                lm_list = detector.find_position(frame, draw=False)
                world_lms = detector.find_world_pose()
                
                # Calculate Angles needed for Analytics
                r_knee = 180
                r_hip = 180
                if len(lm_list) != 0:
                    r_knee = detector.find_angle(frame, 24, 26, 28, draw=True)
                    r_hip = detector.find_angle(frame, 12, 24, 26, draw=True)
                    # Visual balance
                    detector.find_angle(frame, 23, 25, 27, draw=False) 

                if world_lms and not is_paused:
                    fps = 30 
                    analyzer.update(world_lms, fps, r_knee, r_hip)
                
                # Update analyzer with current angles for real-time display if not updated in update()
                analyzer.current_knee_angle = r_knee
                analyzer.current_hip_angle = r_hip

                ret, buffer = cv2.imencode('.jpg', frame)
                last_frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + last_frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/metrics')
def metrics():
    # Calculate score on the fly
    score = scorer.calculate_score(analyzer)
    feedback = scorer.feedback
    
    return jsonify({
        'step_count': analyzer.step_count,
        'cadence': int(analyzer.cadence),
        'stride_length': round(analyzer.stride_length, 2),
        'symmetry_l': int(analyzer.left_symmetry),
        'symmetry_r': int(analyzer.right_symmetry),
        'gct': int(analyzer.gct),
        'score': score,
        'feedback': feedback,
        'hip_angle': int(analyzer.current_hip_angle),
        'knee_angle': int(analyzer.current_knee_angle)
    })

@app.route('/upload_video', methods=['POST'])
def upload_video():
    global video_source, cap, analyzer, scorer, current_mode, is_paused
    if 'file' not in request.files: return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'error': 'No file'}), 400
    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        video_source = filepath
        current_mode = 'video'
        is_paused = False
        
        init_detector('video')
        
        if cap: cap.release()
        cap = cv2.VideoCapture(video_source)
        analyzer = GaitAnalyzer() # Reset
        scorer = AthleticScorer()
        return jsonify({'success': True})

@app.route('/upload_image', methods=['POST'])
def upload_image():
    global static_image_path, current_mode, analyzer, is_paused
    if 'file' not in request.files: return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'error': 'No file'}), 400
    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        static_image_path = filepath
        current_mode = 'image'
        is_paused = False
        init_detector('image')
        return jsonify({'success': True})

@app.route('/set_youtube', methods=['POST'])
def set_youtube():
    global video_source, cap, analyzer, scorer, current_mode, is_paused
    data = request.json
    url = data.get('url')
    if not url: return jsonify({'error': 'No URL'}), 400
    
    print(f"Received YouTube Request: {url}")
    stream_url = get_youtube_stream_url(url)
    
    if not stream_url: 
        print("Failed to get stream URL")
        return jsonify({'error': 'Extraction Failed. Check URL or Server Logs.'}), 400
        
    # Validation: Try to open logic
    temp_cap = cv2.VideoCapture(stream_url)
    if not temp_cap.isOpened():
        print("CV2 Failed to open stream URL")
        return jsonify({'error': 'Video stream unreadable by server.'}), 400
    temp_cap.release()

    video_source = stream_url
    current_mode = 'youtube'
    is_paused = False
    
    init_detector('video')
    
    if cap: cap.release()
    cap = cv2.VideoCapture(video_source)
    analyzer = GaitAnalyzer()
    scorer = AthleticScorer()
    print("YouTube Stream Set Successfully")
    return jsonify({'success': True})

@app.route('/use_camera', methods=['POST'])
def use_camera():
    global video_source, cap, analyzer, scorer, current_mode, is_paused
    data = request.json or {}
    source_input = data.get('source', '0')
    try:
        if isinstance(source_input, str) and source_input.isdigit():
            video_source = int(source_input)
        elif isinstance(source_input, int):
             video_source = source_input
        else:
             video_source = source_input
    except ValueError:
        video_source = 0

    current_mode = 'video'
    is_paused = False
    init_detector('video')
    if cap: cap.release()
    cap = cv2.VideoCapture(video_source)
    analyzer = GaitAnalyzer()
    scorer = AthleticScorer()
    return jsonify({'success': True, 'source': video_source})

@app.route('/control/pause', methods=['POST'])
def pause_video():
    global is_paused
    is_paused = True
    return jsonify({'success': True})

@app.route('/control/resume', methods=['POST'])
def resume_video():
    global is_paused
    is_paused = False
    return jsonify({'success': True})

@app.route('/control/replay', methods=['POST'])
def replay_video():
    global cap, video_source, is_paused
    if cap: cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    is_paused = False
    return jsonify({'success': True})

@app.route('/reset', methods=['POST'])
def reset():
    global analyzer, scorer
    analyzer = GaitAnalyzer()
    scorer = AthleticScorer()
    return jsonify({'success': True})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
