import cv2

def returnCameraIndexes():
    # Cek index 0 sampai 5
    index = 0
    arr = []
    print("Sedang memeriksa kamera yang tersedia... (Mungkin memakan waktu)")
    while index < 6:
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW) # DSHOW for Windows faster checking
        if cap.read()[0]:
            arr.append(index)
            cap.release()
        index += 1
    return arr

def main():
    print("Mencari index kamera yang aktif...")
    cameras = returnCameraIndexes()
    
    if not cameras:
        print("Tidak ada kamera yang terdeteksi.")
        return

    print(f"\nKamera ditemukan pada index: {cameras}")
    print("Mari kita coba lihat isinya satu per satu.")

    for cam_idx in cameras:
        print(f"--- Membuka Kamera Index {cam_idx} ---")
        print("Tekan 'q' untuk lanjut ke kamera berikutnya (atau keluar).")
        
        cap = cv2.VideoCapture(cam_idx)
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Gagal membaca frame.")
                break
            
            cv2.putText(frame, f'Index: {cam_idx}', (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow(f'Test Camera Index {cam_idx}', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
    
    print("\nPemeriksaan selesai.")
    print("Gunakan index kamera yang menampilkan DroidCam Anda saat menjalankan main.py.")

if __name__ == "__main__":
    main()
