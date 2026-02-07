import cv2
import yt_dlp
import time

def test_youtube(url):
    print(f"Testing URL: {url}")
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True
    }
    
    stream_url = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Extracting info...")
            info = ydl.extract_info(url, download=False)
            stream_url = info.get('url')
            print(f"Extraction successful. Stream URL length: {len(stream_url) if stream_url else 0}")
    except Exception as e:
        print(f"Extraction failed: {e}")
        return

    if stream_url:
        print("Attempting to open with cv2...")
        cap = cv2.VideoCapture(stream_url)
        if not cap.isOpened():
            print("FAILED to open video capture.")
        else:
            success, frame = cap.read()
            if success:
                print("SUCCESS: Read frame capabilities verified.")
                print(f"Frame shape: {frame.shape}")
            else:
                print("FAILED to read first frame.")
            cap.release()
    else:
        print("No stream URL found.")

if __name__ == "__main__":
    # Test with a standard vertical running video or standard video
    test_youtube("https://www.youtube.com/watch?v=aqz-KE-bpKQ") # Big Buck Bunny or similar
