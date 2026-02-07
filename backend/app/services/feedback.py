from typing import List, Dict

def get_feedback(metrics: Dict) -> List[str]:
    """
    Generates coaching feedback based on biomechanical metrics.
    """
    feedback = []
    
    # 1. Cadence Analysis
    cadence = metrics.get('cadence', 0)
    if cadence > 0:
        if cadence < 160:
            feedback.append("⚠️ Tingkatkan Cadence! Cobalah langkah lebih cepat dan pendek (>160 spm).")
        elif cadence > 190:
            feedback.append("⚠️ Cadence sangat tinggi. Pastikan langkah tetap efisien.")
        else:
            feedback.append("✅ Cadence optimal (160-190 spm). Pertahankan!")

    # 2. Upper Body Analysis
    biomechanics = metrics.get('biomechanics', {})
    trunk_angle = biomechanics.get('trunk_angle', 0)
    arm_angle = biomechanics.get('arm_angle', 0)

    if trunk_angle > 15:
        feedback.append("⚠️ Tubuh terlalu condong ke depan. Tegapkan punggung Anda.")
    elif trunk_angle < 0:
        feedback.append("⚠️ Tubuh condong ke belakang. Condongkan sedikit ke depan dari pergelangan kaki.")
    
    if arm_angle > 110:
        feedback.append("⚠️ Siku terlalu lurus saat mengayun. Tekuk siku ~90 derajat.")
    
    # 3. Knee Lift (Hip Flexion) - checking raw graph data if available, or just generic advice if error is high
    errors = metrics.get('errors', {})
    hip_error = errors.get('hip_stability', 0)
    if hip_error > 40:
        feedback.append("⚠️ Stabilitas Pinggul rendah. Pastikan lutut diangkat sejajar saat lari.")

    # Limit to top 3 priority messages
    return feedback[:3]
