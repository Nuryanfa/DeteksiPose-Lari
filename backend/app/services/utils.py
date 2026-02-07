import math
import numpy as np

def calculate_angle(a, b, c):
    """
    Menghitung sudut antara tiga titik (a, b, c).
    b adalah titik sudut (misal: siku dikelilingi oleh bahu dan pergelangan tangan).
    a, b, c diharapkan berupa list atau tuple [x, y].
    """
    a = np.array(a) # Titik pertama
    b = np.array(b) # Titik tengah (sudut)
    c = np.array(c) # Titik ketiga
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle
