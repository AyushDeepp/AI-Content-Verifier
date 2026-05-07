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
from core.key_rotator import get_groq_rotator, get_gemini_rotator, get_grok_rotator

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


# --- ENGINE 3: VISION FORENSICS (Gemini + Groq Fallback) ---

async def analyze_frames_with_vision(frames: list) -> str:

    """
    Analyzes video frames using available Vision AI (Gemini primary).
    """
    if not frames:
        return "Visual analysis unavailable."

    # Try Gemini first (Primary)
    gemini_keys = get_gemini_rotator()
    if gemini_keys.has_keys:
        try:
            for model_name in ['gemini-flash-latest', 'gemini-1.5-flash']:
                for attempt in range(gemini_keys.count):
                    try:
                        genai.configure(api_key=gemini_keys.current)
                        model = genai.GenerativeModel(model_name)
                        response = await asyncio.to_thread(
                            model.generate_content,
                            [
                                "Analyze these sequential video frames for AI generation artifacts (morphing, texture crawl, lighting inconsistencies). "
                                "Is this AI generated? Provide forensic justification.",
                                *frames[:4]
                            ]
                        )
                        logger.info(f"VISION ENGINE (Gemini): Success using {model_name}")
                        return response.text
                    except Exception as e:
                        if "429" in str(e) or "not found" in str(e).lower():
                            gemini_keys.rotate()
                            continue
                        raise
        except Exception as e:
            logger.warning(f"Gemini vision failed, trying Groq: {e}")

    # Try Groq (Fallback)
    groq_keys = get_groq_rotator()
    if groq_keys.has_keys:
        try:
            import base64
            from io import BytesIO
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
                "text": """Perform forensic analysis of these frames for AI generation artifacts (morphing, texture crawl)."""
            })
            
            for attempt in range(groq_keys.count):
                try:
                    client = AsyncGroq(api_key=groq_keys.current)
                    model_to_use = "meta-llama/llama-4-scout-17b-16e-instruct"
                    response = await client.chat.completions.create(
                        model=model_to_use,
                        messages=[{"role": "user", "content": image_contents}],
                        max_tokens=500
                    )
                    findings = response.choices[0].message.content
                    logger.info(f"VISION ENGINE (Groq): Success")
                    return findings
                except Exception as e:
                    if "429" in str(e):
                        groq_keys.rotate()
                        continue
                    raise
        except Exception as e:
            logger.error(f"Groq vision fallback failed: {e}")

    return "Visual frame analysis unavailable — relying on motion physics signals only."


# --- ENGINE 4: FORENSIC SYNTHESIZER ---

async def synthesize_verdict(
    visual_findings: str,
    smi_score: float,
    audio_result: Dict[str, Any],
    metadata_result: Dict[str, Any]
) -> Dict[str, Any]:
    """Uses Gemini (Primary) or Groq/Grok to synthesize all signals into a final verdict."""
    gemini_keys = get_gemini_rotator()
    groq_keys = get_groq_rotator()
    grok_keys = get_grok_rotator()
    
    meta_str = f"ALERT: AI signatures found — {', '.join(metadata_result['signatures'])}" \
               if metadata_result['has_ai_metadata'] else "No AI signatures in metadata."
    
    audio_str = f"Audio: {audio_result['label']} (score: {audio_result['score']:.2f})"
    
    prompt = f"""You are a Lead Digital Forensic Analyst. Assess if this video is AI-generated.

FORENSIC EVIDENCE:
1. Visual Frame Analysis: {visual_findings[:500]}
2. Optical Flow (SMI): {smi_score:.3f} [0=natural, 1=AI-like turbulence]
3. {audio_str}
4. Metadata: {meta_str}

Respond ONLY with this JSON:
{{
  "verdict": "AI-Generated" | "Human-Created",
  "confidence": 0.0-1.0,
  "summary": "One sentence forensic justification"
}}"""

    # Try Gemini Synthesis first (Primary)
    if gemini_keys.has_keys:
        try:
            for model_name in ['gemini-flash-latest', 'gemini-1.5-flash']:
                for attempt in range(gemini_keys.count):
                    try:
                        genai.configure(api_key=gemini_keys.current)
                        model = genai.GenerativeModel(model_name)
                        response = await asyncio.to_thread(
                            model.generate_content,
                            prompt
                        )
                        # Robust JSON parsing for older SDKs
                        text = response.text
                        json_match = re.search(r'\{.*\}', text, re.DOTALL)
                        if json_match:
                            result = json.loads(json_match.group(0))
                            logger.info(f"SYNTHESIS ENGINE (Gemini): {result['verdict']}")
                            return result
                        return None

                    except Exception as e:
                        if "429" in str(e):
                            gemini_keys.rotate()
                            continue
                        raise
        except Exception as e:
            logger.warning(f"Gemini synthesis failed, trying Groq: {e}")

    # Fallback to Groq/Grok
    use_grok = grok_keys.has_keys
    keys = grok_keys if use_grok else groq_keys
    
    if keys.has_keys:
        try:
            for attempt in range(keys.count):
                try:
                    if use_grok:
                        from openai import AsyncOpenAI
                        client = AsyncOpenAI(api_key=keys.current, base_url="https://api.x.ai/v1")
                        model = "grok-4.3"
                    else:
                        client = AsyncGroq(api_key=keys.current)
                        model = "llama-3.3-70b-versatile"

                    response = await client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=model,
                        response_format={"type": "json_object"},
                        max_tokens=250
                    )
                    result = json.loads(response.choices[0].message.content)
                    logger.info(f"SYNTHESIS ENGINE ({'Grok' if use_grok else 'Groq'}): {result['verdict']}")
                    return result
                except Exception as e:
                    if "429" in str(e):
                        keys.rotate()
                        continue
                    raise
        except Exception:
            pass

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
        # AvgCV < 1.8 = natural, 1.8-3.0 = borderline, > 3.0 = AI-like
        # We lowered thresholds to catch smoother modern AI (Sora/Kling)
        smi_score = 0.2
        if flow_scores:
            avg_cv = sum(flow_scores) / len(flow_scores)
            if avg_cv < 1.3:
                smi_score = 0.1
            elif avg_cv < 2.0:
                smi_score = 0.2 + (avg_cv - 1.3) * 0.25  # 1.8 -> ~0.32
            elif avg_cv < 3.5:
                smi_score = 0.4 + (avg_cv - 2.0) * 0.30  # 3.0 -> ~0.70
            else:
                smi_score = min(0.95, 0.85 + (avg_cv - 3.5) * 0.05)
            logger.info(f"VIDEO OPTICAL FLOW: AvgCV={avg_cv:.3f}, SMI={smi_score:.3f}")

        # Run all engines in parallel
        audio_task = analyze_audio_forensics(temp_video_path)
        vision_task = analyze_frames_with_vision(frame_images)  # New multi-engine vision

        
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