import google.generativeai as genai
from typing import Dict, Any, List
from core.config import settings
import logging
import tempfile
import os
import cv2
import asyncio
from PIL import Image
from io import BytesIO
import json
import re

logger = logging.getLogger(__name__)

async def detect_ai_video(video_data: bytes) -> Dict[str, Any]:
    """
    Detects AI-generated video using Multi-Frame Temporal Analysis.
    Analyzes 12 representative frames to detect motion inconsistencies.
    """
    if not video_data or len(video_data) == 0:
        return {"result": False, "confidence": 0.5, "error": "Video data empty"}
    
    if not hasattr(settings, 'GEMINI_API_KEY') or not settings.GEMINI_API_KEY:
        return {"result": False, "confidence": 0.5, "error": "API Key missing"}

    temp_video_path = None
    try:
        # 1. Save video to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
            temp_video.write(video_data)
            temp_video_path = temp_video.name
            
        # 2. Extract frames and Calculate Motion Entropy (SMI)
        cap = cv2.VideoCapture(temp_video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0: return {"result": False, "confidence": 0.5, "error": "Invalid video"}

        frame_indices = [int(i * (total_frames - 1) / 11) for i in range(12)]
        frame_images = []
        prev_gray = None
        motion_scores = []
        
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                # Forensic Motion Analysis
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if prev_gray is not None:
                    # Calculate frame difference as a proxy for temporal consistency
                    diff = cv2.absdiff(gray, prev_gray)
                    # AI often has 'shimmering' backgrounds or 'morphing' motion
                    # We measure the entropy of the motion delta
                    motion_score = float(cv2.mean(diff)[0]) / 255.0
                    motion_scores.append(motion_score)
                prev_gray = gray

                # Prepare for Gemini
                frame_res = cv2.resize(frame, (640, 360))
                _, buffer = cv2.imencode('.jpg', frame_res)
                frame_images.append(Image.open(BytesIO(buffer.tobytes())))
        
        cap.release()
        
        # Calculate SMI (Structural Motion Index)
        # Low variance in frame-diff but high overall change is typical of AI 'shimmer'
        smi_score = 0.5
        if motion_scores:
            avg_motion = sum(motion_scores) / len(motion_scores)
            motion_variance = sum((x - avg_motion)**2 for x in motion_scores) / len(motion_scores)
            # High variance in motion delta = Suspicious 'jumpy' AI motion
            smi_score = min(1.0, (motion_variance * 1000) + 0.1) 
            logger.info(f"VIDEO STATS: AvgMotion={avg_motion:.4f}, SMI={smi_score:.4f}")

        # 3. Analyze with Gemini Forensic Auditor
        genai.configure(api_key=settings.GEMINI_API_KEY)
        prompt = """Analyze these 12 frames to detect AI-generation.
1. **Temporal Drift**: Do textures (skin, hair, fabric) 'shimmer' or 'crawl' between frames?
2. **Identity Flux**: Does an object's shape or person's face change subtly as it moves?
3. **Physics Violations**: Does motion look 'liquid' or 'interpolated' rather than solid?

OUTPUT (JSON):
{
  "verdict": "AI-Generated" | "Human-Created",
  "confidence": 0.0-1.0,
  "findings": "reasoning",
  "ai_probability": 0.0-1.0
}
"""
        model_names = ['gemini-2.5-flash', 'gemini-3.1-flash-lite-preview']
        gemini_result = None
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = await asyncio.to_thread(model.generate_content, [prompt] + frame_images)
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    gemini_result = json.loads(json_match.group(0))
                    logger.info(f"GEMINI VIDEO: Success using {model_name}")
                    break
            except: continue
        
        # --- BAYESIAN AGGREGATION ---
        # Weights: Gemini Audit (70%), SMI Physics (30%)
        numerator = 0.0
        denominator = 0.0
        
        # 1. SMI Physics layer
        smi_conf = 0.6 if smi_score > 0.7 else 0.4
        numerator += smi_score * smi_conf * 0.3
        denominator += smi_conf * 0.3
        
        # 2. Gemini Audit layer
        if gemini_result:
            g_score = gemini_result.get("ai_probability", 0.5)
            g_conf = gemini_result["confidence"]
            numerator += g_score * g_conf * 0.7
            denominator += g_conf * 0.7
            
        final_ai_score = numerator / denominator if denominator > 0 else 0.5
        is_ai = final_ai_score > 0.5
        confidence = final_ai_score if is_ai else (1.0 - final_ai_score)

        return {
            "result": is_ai,
            "confidence": float(confidence),
            "ai_score": float(final_ai_score),
            "method": "Temporal Forensic Physics",
            "analysis_details": [
                {
                    "model": "SMI Physics Engine",
                    "verdict": "High Risk" if smi_score > 0.6 else "Normal",
                    "confidence": f"{int(smi_score*100)}%",
                    "analysis": f"Structural Motion Index (SMI) = {smi_score:.2f}. Measured temporal pixel variance."
                },
                {
                    "model": "Temporal Audit",
                    "verdict": gemini_result["verdict"] if gemini_result else "Unknown",
                    "confidence": f"{int(gemini_result['confidence']*100)}%" if gemini_result else "0%",
                    "analysis": gemini_result["findings"] if gemini_result else "Engine unavailable"
                }
            ]
        }
            
    except Exception as e:
        logger.error(f"Video detection failed: {e}")
        return {"result": False, "confidence": 0.5, "error": str(e)}
    finally:
        if temp_video_path and os.path.exists(temp_video_path):
            os.unlink(temp_video_path)
            
    return {"result": False, "confidence": 0.5, "error": "Detection incomplete"}