import tkinter as tk
from gui import PoseApp

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = PoseApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Error launching GUI: {e}")
        print("Pastikan file gui.py ada dan library sudah terinstall.")

