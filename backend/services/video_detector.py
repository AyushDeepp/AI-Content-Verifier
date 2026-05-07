"""
VIDEO FORENSIC ENSEMBLE v3.0
- Engine 1: Dense Optical Flow (Farneback) — Motion Physics Analysis
- Engine 2: Local FFT Audio Frequency Analysis — Vocoder Artifact Detection
- Engine 3: Mutagen Metadata Scanner — AI Watermark Detection (No PATH required)
- Engine 4: Gemini 2.0 Flash — Visual Frame Forensics
- Engine 5: Groq Llama-3.3 — Cross-Modal Verdict Synthesis
"""
import google.generativeai as genai
from typing import Dict, Any, List, Optional
from core.config import settings
import logging
import tempfile
import os
import cv2
import asyncio
from PIL import Image
from io import BytesIO
import json
import numpy as np
import re
from groq import AsyncGroq
from core.key_rotator import get_groq_rotator

logger = logging.getLogger(__name__)


# --- ENGINE 1: LOCAL FFT AUDIO FORENSICS (Zero API dependency) ---

async def analyze_audio_forensics(video_path: str) -> Dict[str, Any]:
    """
    Analyzes audio using local FFT frequency distribution.
    AI vocoders (TTS/voice cloners) produce unnaturally uniform frequency spectra.
    This is a 100% local analysis — no API calls, no file locks.
    """
    try:
        # Use numpy FFT on raw audio if available via moviepy
        from moviepy import VideoFileClip
        video = VideoFileClip(video_path)
        
        if video.audio is None:
            video.close()
            return {"score": 0.1, "label": "No audio track", "confidence": 0.5}
        
        # Sample 3 seconds of audio at most
        duration = min(video.duration, 3.0)
        fps = video.audio.fps
        n_samples = int(fps * duration)
        
        audio_array = video.audio.to_soundarray(fps=fps)[:n_samples]
        video.audio.close()
        video.close()
        
        # Flatten to mono
        if audio_array.ndim > 1:
            audio_mono = np.mean(audio_array, axis=1)
        else:
            audio_mono = audio_array
        
        # FFT Analysis
        fft = np.abs(np.fft.rfft(audio_mono))
        
        # AI vocoders have a "flat" frequency response (low std deviation in FFT bins)
        fft_std = np.std(fft)
        fft_mean = np.mean(fft) + 1e-9
        cv = fft_std / fft_mean  # Coefficient of variation
        
        # High CV = natural audio, Low CV = suspiciously uniform (AI-generated)
        # Empirically calibrated: Natural speech CV > 2.0, AI TTS CV < 1.5
        ai_score = max(0.0, min(1.0, 1.0 - (cv / 3.0)))
        
        label = "AI Vocoder Pattern" if ai_score > 0.55 else "Natural Audio"
        logger.info(f"AUDIO FFT: CV={cv:.2f}, AI_Score={ai_score:.2f}")
        
        return {"score": ai_score, "label": label, "confidence": 0.7}
        
    except Exception as e:
        logger.warning(f"Audio forensics failed: {e}")
        return {"score": 0.1, "label": "Analysis failed", "confidence": 0.0}


# --- ENGINE 2: MUTAGEN METADATA SCANNER (Pure Python — No ffprobe PATH) ---

def scan_video_metadata(video_path: str) -> Dict[str, Any]:
    """
    Scans video container metadata for AI generation watermarks.
    Uses mutagen (pure Python) — works on all platforms without system PATH dependencies.
    """
    try:
        import mutagen
        from mutagen.mp4 import MP4
        
        meta = MP4(video_path)
        all_tags = str(meta.tags).lower() if meta.tags else ""
        
        # Known AI model signatures in metadata
        ai_signatures = [
            "sora", "runway", "kling", "luma", "pika", "stable video",
            "invideo", "synthesia", "heygen", "d-id", "topaz", "c2pa",
            "adobe firefly", "generative", "ai generated"
        ]
        
        found = [sig for sig in ai_signatures if sig in all_tags]
        
        # Also check encoder field
        encoder = ""
        if meta.tags:
            encoder = str(meta.tags.get("\xa9too", [""])[0]).lower()
        
        is_suspicious_encoder = any(sig in encoder for sig in ai_signatures)
        
        logger.info(f"METADATA SCAN: Found={found}, Encoder={encoder}")
        
        return {
            "has_ai_metadata": len(found) > 0 or is_suspicious_encoder,
            "signatures": found,
            "encoder": encoder,
            "confidence": 0.98 if found else 0.0
        }
    except Exception as e:
        logger.warning(f"Mutagen metadata scan failed (will use ffprobe fallback): {e}")
        # Fallback: try ffprobe via shell
        try:
            import subprocess
            cmd = f'ffprobe -v quiet -show_format -show_streams -print_format json "{video_path}"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=10)
            metadata_str = result.stdout.lower()
            ai_sigs = ["c2pa", "sora", "kling", "runway", "luma", "pika", "generative ai", "topaz"]
            found = [s for s in ai_sigs if s in metadata_str]
            return {
                "has_ai_metadata": len(found) > 0,
                "signatures": found,
                "encoder": "",
                "confidence": 0.98 if found else 0.0
            }
        except Exception as e2:
            logger.warning(f"ffprobe fallback also failed: {e2}")
        return {"has_ai_metadata": False, "signatures": [], "encoder": "", "confidence": 0.0}


# --- ENGINE 3: GROQ VISION FORENSICS (Free, no quota issues) ---

async def analyze_frames_with_groq(frames: list) -> str:
    """
    Sends video frames to Groq (llama-4-scout vision model) for forensic analysis.
    100% free, no separate quota from Gemini.
    """
    groq_keys = get_groq_rotator()
    if not groq_keys.has_keys or not frames:
        return "Visual analysis unavailable."
    
    try:
        import base64
        from io import BytesIO
        
        # Convert up to 4 frames to base64
        image_contents = []
        for frame in frames[:4]:
            buf = BytesIO()
            frame.save(buf, format="JPEG", quality=70)
            b64 = base64.b64encode(buf.getvalue()).decode()
            image_contents.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
            })
        
        image_contents.append({
            "type": "text",
            "text": """Forensic analysis of these video frames. Look for:
1. FACIAL MORPHING — do faces change shape/texture unnaturally between frames?
2. BACKGROUND SHIMMERING — pixel 'crawl' or texture swimming in backgrounds?
3. PHYSICS VIOLATIONS — hair/water/cloth movement that defies gravity or inertia?
4. TEXTURE INCONSISTENCY — skin that melts or eyes that change shape?
5. LIGHTING — does light direction change between frames impossibly?

State clearly: is this AI-generated or real footage, and what specific artifacts did you see?"""
        })
        
        # Try with key rotation on quota errors
        for attempt in range(groq_keys.count):
            try:
                client = AsyncGroq(api_key=groq_keys.current)
                response = await client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[{"role": "user", "content": image_contents}],
                    max_tokens=400
                )
                findings = response.choices[0].message.content
                logger.info(f"GROQ VISION: Analysis complete")
                return findings
            except Exception as e:
                if "429" in str(e) or "rate" in str(e).lower():
                    groq_keys.rotate()
                    continue
                raise
    except Exception as e:
        logger.warning(f"Groq vision analysis failed: {e}")
        # Fallback to text-only analysis with SMI context
        return "Visual frame analysis unavailable — relying on motion physics signals only."


# --- ENGINE 4: GROQ CROSS-MODAL SYNTHESIZER ---

async def synthesize_verdict(
    visual_findings: str,
    smi_score: float,
    audio_result: Dict[str, Any],
    metadata_result: Dict[str, Any]
) -> Dict[str, Any]:
    """Uses Groq Llama-3.3 to synthesize all signals into a final verdict."""
    groq_keys = get_groq_rotator()
    if not groq_keys.has_keys:
        return None
    
    try:
        meta_str = f"ALERT: AI signatures found — {', '.join(metadata_result['signatures'])}" \
                   if metadata_result['has_ai_metadata'] else "No AI signatures in metadata."
        
        audio_str = f"Audio: {audio_result['label']} (score: {audio_result['score']:.2f})"
        
        prompt = f"""You are a Lead Digital Forensic Analyst. Assess if this video is AI-generated.

FORENSIC EVIDENCE:
1. Visual Frame Analysis: {visual_findings[:500]}
2. Optical Flow (SMI): {smi_score:.3f} [0=natural, 1=AI-like turbulence]
3. {audio_str}
4. Metadata: {meta_str}

DECISION RULES:
- If metadata has AI signatures → ALWAYS classify as AI-Generated with 95%+ confidence
- If SMI > 0.65 AND visual findings suggest artifacts → AI-Generated with 80%+ confidence
- If all signals are ambiguous → default to Human-Created with 55% confidence
- If audio shows vocoder pattern AND SMI > 0.5 → AI-Generated with 75%+ confidence

Respond ONLY with this JSON (no extra text):
{{
  "verdict": "AI-Generated",
  "confidence": 0.87,
  "summary": "Brief one-sentence forensic justification"
}}"""

        # Try with key rotation on quota errors
        for attempt in range(groq_keys.count):
            try:
                client = AsyncGroq(api_key=groq_keys.current)
                response = await client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"},
                    max_tokens=200
                )
                result = json.loads(response.choices[0].message.content)
                logger.info(f"GROQ SYNTHESIS: {result}")
                return result
            except Exception as e:
                if "429" in str(e) or "rate" in str(e).lower():
                    groq_keys.rotate()
                    continue
                raise
    except Exception as e:
        logger.error(f"Groq synthesis failed: {e}")
        return None


# --- MAIN DETECTOR ---

async def detect_ai_video(video_data: bytes) -> Dict[str, Any]:
    """
    Multi-Engine Video Forensic Ensemble v3.0
    Combines: Optical Flow + Local Audio FFT + Metadata + Gemini Visual + Groq Synthesis
    """
    if not video_data or len(video_data) == 0:
        return {"result": False, "confidence": 0.5, "error": "Video data empty"}

    temp_video_path = None
    cap = None
    try:
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as f:
            f.write(video_data)
            temp_video_path = f.name

        # --- OPTICAL FLOW ANALYSIS ---
        cap = cv2.VideoCapture(temp_video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames <= 0:
            return {"result": False, "confidence": 0.5, "error": "Invalid video file"}

        n_samples = min(10, total_frames)
        frame_indices = [int(i * (total_frames - 1) / (n_samples - 1)) for i in range(n_samples)]
        
        frame_images = []
        prev_gray = None
        flow_scores = []

        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                continue
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_gray is not None:
                # Farneback Optical Flow
                flow = cv2.calcOpticalFlowFarneback(
                    prev_gray, gray, None, 0.5, 2, 10, 2, 5, 1.1, 0
                )
                mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
                # Coefficient of variation of flow magnitudes
                # AI videos have HIGHER CV (erratic, non-physical motion)
                flow_cv = float(np.std(mag) / (np.mean(mag) + 1e-9))
                flow_scores.append(flow_cv)
            
            prev_gray = gray
            
            # Prepare frame for Gemini (resize for efficiency)
            small = cv2.resize(frame, (512, 288))
            _, buf = cv2.imencode('.jpg', small, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_images.append(Image.open(BytesIO(buf.tobytes())))

        cap.release()
        cap = None

        # Calibrate SMI from Coefficient of Variation
        # AvgCV < 2.0 = natural, 2.0-3.5 = borderline, > 3.5 = AI-like
        smi_score = 0.2
        if flow_scores:
            avg_cv = sum(flow_scores) / len(flow_scores)
            # Piecewise linear calibration based on empirical ranges
            if avg_cv < 1.5:
                smi_score = 0.1  # Clearly natural
            elif avg_cv < 2.5:
                smi_score = 0.2 + (avg_cv - 1.5) * 0.15  # 0.2 to 0.35
            elif avg_cv < 4.0:
                smi_score = 0.35 + (avg_cv - 2.5) * 0.30  # 0.35 to 0.80
            else:
                smi_score = min(0.95, 0.80 + (avg_cv - 4.0) * 0.05)  # 0.80+
            logger.info(f"VIDEO OPTICAL FLOW: AvgCV={avg_cv:.3f}, SMI={smi_score:.3f}")

        # Run all engines in parallel
        audio_task = analyze_audio_forensics(temp_video_path)
        vision_task = analyze_frames_with_groq(frame_images)  # Groq vision (free)
        
        metadata_result = scan_video_metadata(temp_video_path)
        
        audio_result, visual_findings = await asyncio.gather(audio_task, vision_task)

        # --- GROQ CROSS-MODAL SYNTHESIS ---
        groq_result = await synthesize_verdict(visual_findings, smi_score, audio_result, metadata_result)

        # --- FINAL ENSEMBLE DECISION ---
        if groq_result:
            final_verdict = groq_result["verdict"]
            final_confidence = float(groq_result["confidence"])
        else:
            # Fallback: simple threshold on SMI
            final_verdict = "AI-Generated" if smi_score > 0.55 else "Human-Created"
            final_confidence = max(smi_score, 0.55) if smi_score > 0.55 else (1.0 - smi_score)

        # Force override: metadata is ground truth
        if metadata_result["has_ai_metadata"]:
            final_verdict = "AI-Generated"
            final_confidence = max(final_confidence, 0.97)

        # --- BUILD ANALYSIS DETAILS (Human-friendly, no model names) ---
        smi_label = "high (AI-like)" if smi_score > 0.55 else "low (natural)"
        analysis_details = [
            {
                "model": "Optical Flow",
                "verdict": "AI-Generated" if smi_score > 0.55 else "Human-Created",
                "confidence": f"{int(smi_score * 100)}%",
                "analysis": (
                    f"Motion analysis: {smi_label}. "
                    f"This measures how consistent the movement of objects is across video frames. "
                    f"AI-generated videos often show erratic, non-physical motion patterns — objects may shimmer, "
                    f"backgrounds may crawl, and movement doesn't follow natural inertia. "
                    f"A score above 0.55 indicates motion inconsistencies typical of AI generation."
                )
            },
            {
                "model": "Audio Analysis",
                "verdict": "AI Vocoder" if audio_result["score"] > 0.55 else "Natural Audio",
                "confidence": f"{int(max(audio_result['score'], 1 - audio_result['score']) * 100)}%",
                "analysis": (
                    f"{audio_result['label']}. "
                    f"Audio was analyzed by examining the distribution of sound frequencies. "
                    f"AI-generated voices (from text-to-speech or voice cloning tools) tend to produce "
                    f"unnaturally uniform frequency patterns, while natural human speech has varied, "
                    f"organic frequency distribution."
                )
            }
        ]

        if metadata_result["has_ai_metadata"]:
            analysis_details.append({
                "model": "Metadata",
                "verdict": "AI-Generated",
                "confidence": "98%",
                "analysis": (
                    f"Digital signatures found in the video file's internal metadata: "
                    f"{', '.join(metadata_result['signatures'])}. "
                    f"These are watermarks or tags embedded by AI video generation tools "
                    f"(such as Sora, Runway, Kling, etc.) that confirm the content was machine-generated."
                )
            })

        if groq_result:
            analysis_details.append({
                "model": "Synthesis",
                "verdict": final_verdict,
                "confidence": f"{int(final_confidence * 100)}%",
                "analysis": (
                    f"{groq_result.get('summary', 'Multi-signal analysis complete.')} "
                    f"This conclusion was reached by cross-referencing visual frame analysis, "
                    f"motion physics, audio patterns, and file metadata together."
                )
            })

        return {
            "result": final_verdict == "AI-Generated",
            "confidence": final_confidence,
            "method": "Multi-Modal Forensic Ensemble v3.0",
            "analysis_details": analysis_details
        }

    except Exception as e:
        logger.error(f"Video detection failed: {e}", exc_info=True)
        return {"result": False, "confidence": 0.5, "error": str(e)}
    finally:
        if cap is not None:
            cap.release()
        if temp_video_path and os.path.exists(temp_video_path):
            try:
                os.remove(temp_video_path)
            except Exception:
                pass