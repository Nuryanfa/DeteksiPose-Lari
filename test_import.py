try:
    import yt_dlp
    print("yt_dlp imported successfully")
except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
