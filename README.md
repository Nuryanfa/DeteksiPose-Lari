# Deteksi3d: Smart Sprint Training System (SSTS)

**Deteksi3d** (juga dikenal sebagai SSTS) adalah sistem analisis biomekanik berbasis *Artificial Intelligence* (AI) yang dirancang untuk meningkatkan performa atlet sprint 100 meter. Sistem ini menggunakan teknologi *Computer Vision* untuk menganalisis gerakan atlet secara real-time maupun dari rekaman video, memberikan data yang presisi bagi pelatih dan manajemen olahraga (seperti KONI) untuk pengambilan keputusan berbasis data.

![SSTS Overview](https://img.shields.io/badge/Status-Development-blue) ![Python](https://img.shields.io/badge/Python-3.10+-yellow) ![React](https://img.shields.io/badge/Frontend-React-61DAFB) ![License](https://img.shields.io/badge/License-MIT-green)

## 🚀 Fitur Utama

Sistem ini terdiri dari dua komponen utama: **Edge AI Processing** dan **Web Dashboard**.

### 1. Analisis Biomekanik (Edge AI)
Menggunakan kamera standar untuk mengekstrak metrik kunci tanpa memerlukan sensor yang dipasang di tubuh (markerless).
- **Pose Estimation**: Melacak 33 titik sendi tubuh menggunakan MediaPipe.
- **Real-time Metrics**: Menghitung *Cadence* (langkah/menit), *Stride Length* (panjang langkah), dan *Ground Contact Time* (GCT).
- **Gait Analysis**: Menganalisis simetri langkah kaki kiri vs kanan dan sudut sendi (lutut, pinggul).
- **Auto Event Detection**: Mendeteksi fase lari (Start, Drive, Max Velocity).

### 2. Dashboard Pelatih & Manajemen (Web)
Platform berbasis web untuk visualisasi data dan manajemen atlet.
- **Coach Dashboard**: Analisis mikro per atlet, pemutar video dengan overlay grafik, dan perbandingan performa antar sesi.
- **Management Dashboard**: Analisis makro untuk memantau perkembangan seluruh atlet binaan, pemetaan bakat, dan statistik cedera.
- **Manajemen Data**: CRUD untuk data atlet, pelatih, dan sesi latihan.

## 🛠️ Teknologi yang Digunakan

### Backend & AI
- **Python**: Bahasa pemrograman utama.
- **FastAPI**: Framework API modern dan cepat untuk komunikasi antara Edge dan Frontend.
- **MediaPipe & OpenCV**: Library inti untuk pemrosesan citra dan deteksi pose.
- **SQLite / PostgreSQL**: Penyimpanan data pengguna dan hasil analisis.

### Frontend
- **React.js (Vite)**: Framework UI untuk dashboard yang responsif.
- **Tailwind CSS**: Framework CSS untuk styling modern dan cepat.
- **Recharts**: Library untuk visualisasi data grafik interaktif.

## 🤝 Kontribusi
Kontribusi sangat diterima! Silakan buat *Fork* repository ini, lakukan perubahan pada branch fitur Anda, dan kirimkan *Pull Request*.

## 📄 Lisensi
Project ini dilisensikan di bawah [MIT License](LICENSE).

---
*Dikembangkan untuk mendukung kemajuan teknologi olahraga Indonesia.*
