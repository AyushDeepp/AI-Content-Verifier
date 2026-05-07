import httpx
import google.generativeai as genai
from typing import Dict, Any, Optional, List
import exifread
from core.config import settings
import logging
import asyncio
import base64
from io import BytesIO
from PIL import Image
from huggingface_hub import InferenceClient
import json
import re

from core.key_rotator import get_gemini_rotator, get_groq_rotator
from groq import AsyncGroq

logger = logging.getLogger(__name__)

# --- ENGINE 1: HUGGING FACE VISION CLASSIFIERS ---

async def query_hf_image_model(model_id: str, image_bytes: bytes, api_key: str) -> Optional[float]:
    """Queries a Hugging Face image classification model via official InferenceClient"""
    if not api_key:
        return None
        
    try:
        # Direct HTTP request is more reliable for image bytes than the SDK in some environments
        url = f"https://router.huggingface.co/hf-inference/models/{model_id}"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "image/jpeg" # Standard for binary inference
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, content=image_bytes, timeout=30.0)
            
        if response.status_code == 200:
            result = response.json()
            ai_score = 0.0
            for item in result:
                label = item.get("label", "").lower()
                score = item.get("score", 0.0)
                if any(k in label for k in ["ai", "generated", "synthetic", "fake", "label_1"]):
                    ai_score = score
                    break
                elif any(k in label for k in ["real", "human", "photograph", "label_0"]):
                    ai_score = 1.0 - score
                    break
            
            logger.info(f"HF IMAGE ENGINE ({model_id}): Score={ai_score:.2f}")
            return ai_score
        else:
            logger.warning(f"HF Image API Error ({model_id}): {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.warning(f"HF Image Inference Error ({model_id}): {e}")
        return None
    return None

# --- ENGINE 2: FORENSIC METADATA ANALYSIS (LOCAL) ---

def check_image_metadata(image_bytes: bytes) -> Dict[str, Any]:
    """Scans EXIF and XMP data for AI generation signatures"""
    try:
        tags = exifread.process_file(BytesIO(image_bytes))
        signatures = {
            "Software": ["Midjourney", "DALL-E", "Stable Diffusion", "Adobe Firefly"],
            "Description": ["AI generated", "Artificial Intelligence", "Midjourney"],
            "Comment": ["AI-generated", "Synthetic"]
        }
        
        found_markers = []
        for tag_name, tag_value in tags.items():
            for field, markers in signatures.items():
                if field in str(tag_name):
                    for marker in markers:
                        if marker.lower() in str(tag_value).lower():
                            found_markers.append(f"{tag_name}: {marker}")
        
        return {
            "has_ai_metadata": len(found_markers) > 0,
            "markers": found_markers,
            "confidence": 0.95 if found_markers else 0.0
        }
    except Exception as e:
        logger.warning(f"Metadata scan failed: {e}")
        return {"has_ai_metadata": False, "markers": [], "confidence": 0.0}

# --- ENGINE 3: SIGHTENGINE API (EXTERNAL) ---

async def query_sightengine(image_bytes: bytes) -> Optional[float]:
    """Queries Sightengine AI detection API (requires API keys)"""
    if not settings.SIGHTENGINE_API_USER or not settings.SIGHTENGINE_API_SECRET:
        return None
        
    try:
        url = "https://api.sightengine.com/1.0/check.json"
        data = {
            'models': 'genai',
            'api_user': settings.SIGHTENGINE_API_USER,
            'api_secret': settings.SIGHTENGINE_API_SECRET
        }
        files = {'media': image_bytes}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data, files=files)
            
        if response.status_code == 200:
            result = response.json()
            # Sightengine returns probability of being AI-generated
            return result.get('type', {}).get('ai_generated', 0.0)
    except Exception as e:
        logger.error(f"Sightengine API failed: {e}")
    return None

# --- ENGINE 2: GEMINI VISION FORENSICS ---

async def get_gemini_vision_forensics(image_data: bytes) -> Dict[str, Any]:
    """Uses Gemini Vision to identify specific AI artifacts in an image"""
    if not hasattr(settings, 'GEMINI_API_KEY') or not settings.GEMINI_API_KEY:
        return None
        
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        
        image = Image.open(BytesIO(image_data))
        
        prompt = """You are a Visual Forensic Expert. Analyze this image to detect AI-generation.
        
FORENSIC CRITERIA:
1. **Logo & Vector Perfection**: AI logos are often 'too mathematically perfect' with unnatural symmetry or gradients that lack brush/vector-path artifacts.
2. **Text Anomalies**: Look for nonsensical text, blurred letters, or 'alien' symbols within the design.
3. **Diffusion Noise**: Check for subtle 'grain' patterns or blurring at high-contrast edges (common in AI).
4. **Logical Consistency**: Look for lighting that doesn't follow a source, or 'impossible' shadows.

OUTPUT FORMAT (JSON):
{
  "verdict": "AI-Generated" | "Human-Created",
  "confidence": 0.0-1.0,
  "anomalies": ["list of specific visual artifacts found"],
  "score_ai": 0.0-1.0
}
"""
        gemini_keys = get_gemini_rotator()
        if not gemini_keys.has_keys:
            return None
        
        # Try models with key rotation on quota errors
        response = None
        for model_name in ['gemini-flash-latest', 'gemini-2.0-flash-lite', 'gemini-2.0-flash']:
            for attempt in range(gemini_keys.count):
                try:
                    genai.configure(api_key=gemini_keys.current)
                    model = genai.GenerativeModel(model_name)
                    response = await asyncio.to_thread(model.generate_content, [prompt, image])
                    if response:
                        logger.info(f"GEMINI VISION ENGINE: Success using {model_name}")
                        break
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        gemini_keys.rotate()
                        continue
                    logger.warning(f"Gemini {model_name} unavailable: {e}")
                    break  # Non-quota error, try next model
            if response:
                break
        
        if not response:
            return None
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except Exception as e:
        logger.error(f"Gemini vision forensics failed: {e}")
    return None


# --- ENGINE 2b: GROQ VISION FALLBACK ---

async def get_groq_vision_forensics(image_data: bytes) -> Dict[str, Any]:
    """Fallback: Uses Groq Llama-4-Scout vision model when Gemini is unavailable."""
    groq_keys = get_groq_rotator()
    if not groq_keys.has_keys:
        return None
    
    try:
        import base64
        img = Image.open(BytesIO(image_data))
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=75)
        b64 = base64.b64encode(buf.getvalue()).decode()
        
        content = [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
            },
            {
                "type": "text",
                "text": """Analyze this image to detect if it's AI-generated. Look for:
1. Unnatural perfection or symmetry
2. Text anomalies (gibberish, warped letters)
3. Lighting/shadow inconsistencies
4. Skin/texture smoothness typical of AI
5. Background artifacts or blending errors

Respond ONLY with JSON:
{"verdict": "AI-Generated" or "Human-Created", "confidence": 0.0-1.0, "anomalies": ["list"], "score_ai": 0.0-1.0}"""
            }
        ]
        
        for attempt in range(groq_keys.count):
            try:
                client = AsyncGroq(api_key=groq_keys.current)
                response = await client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[{"role": "user", "content": content}],
                    max_tokens=300
                )
                text = response.choices[0].message.content
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(0))
                    logger.info(f"GROQ VISION FALLBACK: verdict={result.get('verdict')}, score={result.get('score_ai')}")
                    return result
                return None
            except Exception as e:
                if "429" in str(e) or "rate" in str(e).lower():
                    groq_keys.rotate()
                    continue
                raise
    except Exception as e:
        logger.warning(f"Groq vision fallback failed: {e}")
    return None

# --- ENGINE 4: ERROR LEVEL ANALYSIS (ELA) (LOCAL) ---

def calculate_ela_score(image_bytes: bytes, quality: int = 90) -> float:
    """Detects compression inconsistencies typical of manipulated or AI images"""
    try:
        original = Image.open(BytesIO(image_bytes)).convert('RGB')
        
        # Save at lower quality and re-open
        buffer = BytesIO()
        original.save(buffer, format='JPEG', quality=quality)
        buffer.seek(0)
        resaved = Image.open(buffer)
        
        # Calculate absolute difference
        from PIL import ImageChops
        diff = ImageChops.difference(original, resaved)
        
        # Scale the difference to make it visible
        extrema = diff.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        if max_diff == 0: max_diff = 1
        scale = 255.0 / max_diff
        
        # Calculate average "error" brightness
        import numpy as np
        diff_arr = np.array(diff)
        avg_diff = np.mean(diff_arr)
        
        # ELA LOGIC:
        # AI images (GAN/Diffusion) have extremely UNIFORM compression response → LOW avg_diff
        # Real/manipulated photos have HIGH avg_diff (uneven compression artifacts)
        # So: LOW avg_diff → HIGH AI probability
        
        # Normalize: if avg_diff is below 5, the image is suspiciously uniform (AI-like)
        ai_probability = max(0.0, min(1.0, 1.0 - (avg_diff / 8.0)))
        return float(ai_probability)
    except Exception as e:
        logger.warning(f"ELA calculation failed: {e}")
        return 0.5

# --- ENSEMBLE ORCHESTRATOR ---

async def detect_ai_image(image_data: bytes) -> Dict[str, Any]:
    """
    Enhanced image detection using Multi-Engine Ensemble.
    """
    if not image_data or len(image_data) == 0:
        return {"result": False, "confidence": 0.5, "error": "Image data empty"}
    
    # 1. Prepare and resize image for efficiency
    try:
        img = Image.open(BytesIO(image_data))
        # Resize if too large (max 1024px)
        if max(img.size) > 1024:
            img.thumbnail((1024, 1024))
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            image_data = buffer.getvalue()
    except Exception as e:
        return {"result": False, "confidence": 0.5, "error": f"Invalid image: {e}"}

    # 2. Query engines in parallel
    hf_models = [
        "haywoodsloan/ai-image-detector-dev-deploy",
        "Organika/sdxl-detector"
    ]
    
    hf_tasks = [query_hf_image_model(m, image_data, settings.HUGGINGFACE_API_KEY) for m in hf_models]
    gemini_task = get_gemini_vision_forensics(image_data)
    sight_task = query_sightengine(image_data)
    
    # 3. Local Forensic Scan (Instant)
    metadata_result = check_image_metadata(image_data)
    ela_score = calculate_ela_score(image_data)
    
    hf_results, gemini_result, sight_score = await asyncio.gather(
        asyncio.gather(*hf_tasks),
        gemini_task,
        sight_task
    )
    
    # If Gemini failed (quota), fall back to Groq vision
    if gemini_result is None:
        logger.info("Gemini unavailable, using Groq vision fallback for image analysis")
        gemini_result = await get_groq_vision_forensics(image_data)
    
    valid_hf_scores = [s for s in hf_results if s is not None]
    hf_score = sum(valid_hf_scores) / len(valid_hf_scores) if valid_hf_scores else None
    
    # --- WEIGHTED ENSEMBLE ---
    
    ensemble_ai_score = 0.0
    total_active_weight = 0.0
    
    # Bayesian Weights by Reliability
    # Vision AI (40%), Neural HF (25%), Sightengine (20%), ELA (15%)
    weights = {"hf": 0.25, "gemini": 0.40, "sight": 0.2, "ela": 0.15}
    
    numerator = 0.0
    denominator = 0.0
    
    # Extract vision result for cross-checking
    vision_says_ai = False
    vision_score = 0.0
    if gemini_result:
        vision_score = gemini_result.get("score_ai", 
            gemini_result["confidence"] if gemini_result["verdict"] == "AI-Generated" else (1.0 - gemini_result["confidence"]))
        vision_says_ai = gemini_result["verdict"] == "AI-Generated" and gemini_result["confidence"] > 0.6
    
    # 1. Local Physics Engine (ELA)
    numerator += ela_score * 0.8 * weights["ela"]
    denominator += 0.8 * weights["ela"]
    
    # 2. Metadata Signal (Force Multiplier)
    meta_weight = 0.0
    if metadata_result["has_ai_metadata"]:
        # If we find explicit AI metadata, we treat it as very high confidence AI
        numerator += 0.98 * 1.0 # 98% AI score
        denominator += 1.0
        meta_weight = 1.0 # Boost this result
    
    if hf_score is not None:
        # BLIND-SPOT PENALTY: If vision model confidently says AI but HF says Human,
        # reduce HF weight — these classifiers are trained on older generators and
        # miss newer AI images (Midjourney v6, DALL-E 3, Flux, etc.)
        hf_conf = 0.7
        if hf_score < 0.2 and vision_says_ai:
            logger.warning("Vision detected AI but HF classifiers missed it — applying blind-spot penalty to HF.")
            hf_conf = 0.2  # Drastically reduce HF influence
        
        numerator += hf_score * hf_conf * weights["hf"]
        denominator += hf_conf * weights["hf"]
        
    if gemini_result:
        g_verdict = gemini_result["verdict"]
        g_conf = gemini_result["confidence"]
        g_score = gemini_result.get("score_ai", g_conf if g_verdict == "AI-Generated" else (1.0 - g_conf))
        
        g_reliability = g_conf
            
        numerator += g_score * g_reliability * weights["gemini"]
        denominator += g_reliability * weights["gemini"]

    if sight_score is not None:
        numerator += sight_score * 0.9 * weights["sight"]
        denominator += 0.9 * weights["sight"]
        
    final_ai_score = numerator / denominator if denominator > 0 else 0.5
    
    logger.info(f"IMAGE FORENSIC ENSEMBLE: Score={final_ai_score:.2f}, Reliability={denominator:.2f}")
    
    is_ai = final_ai_score > 0.5
    confidence = final_ai_score if is_ai else (1.0 - final_ai_score)
    
    # Build detailed analysis
    analysis_details = []
    if hf_score is not None:
        analysis_details.append({
            "model": "Neural Classifier",
            "verdict": "AI-Generated" if hf_score > 0.5 else "Human-Created",
            "confidence": f"{int(max(hf_score, 1-hf_score)*100)}%",
            "analysis": (
                f"The image was scanned for pixel-level patterns invisible to the human eye. "
                f"AI-generated images contain unique frequency artifacts left behind by neural networks "
                f"(such as GAN fingerprints or diffusion noise patterns) that distinguish them from real photographs."
            )
        })
        
    if gemini_result:
        anoms = gemini_result.get("anomalies", [])
        analysis_details.append({
            "model": "Visual Forensics",
            "verdict": gemini_result["verdict"],
            "confidence": f"{int(gemini_result['confidence']*100)}%",
            "analysis": (
                f"Visual inspection findings: {', '.join(anoms) if anoms else 'No obvious structural anomalies found.'} "
                f"This analysis examines the image for tell-tale signs of AI generation — such as "
                f"unnaturally perfect symmetry, impossible lighting/shadows, text anomalies, "
                f"and diffusion noise patterns at high-contrast edges."
            )
        })
    
    if metadata_result["has_ai_metadata"]:
        analysis_details.append({
            "model": "Metadata",
            "verdict": "AI-Generated",
            "confidence": "95%",
            "analysis": (
                f"AI software signatures found in the image file's embedded metadata: "
                f"{', '.join(metadata_result['markers'])}. "
                f"This confirms the image was created using an AI generation tool."
            )
        })
        
    if sight_score is not None:
        analysis_details.append({
            "model": "Deep Analysis",
            "verdict": "AI-Generated" if sight_score > 0.5 else "Human-Created",
            "confidence": f"{int(max(sight_score, 1-sight_score)*100)}%",
            "analysis": (
                f"A specialized neural network independently analyzed the image for generative AI patterns."
            )
        })
        
    ela_label = "suspicious (AI-like uniformity)" if ela_score > 0.6 else "normal (natural compression)"
    analysis_details.append({
        "model": "Compression Analysis",
        "verdict": "Suspicious" if ela_score > 0.6 else "Normal",
        "confidence": f"{int(ela_score*100)}%",
        "analysis": (
            f"Compression consistency: {ela_label}. "
            f"This technique re-saves the image and measures how uniformly it compresses. "
            f"AI-generated images compress very uniformly (they were never 'real' photos), "
            f"while genuine photographs show varied compression artifacts across different regions."
        )
    })
        
    return {
        "result": is_ai,
        "confidence": float(confidence),
        "ai_score": float(final_ai_score),
        "real_score": float(1.0 - final_ai_score),
        "method": "Multi-Engine Ensemble",
        "analysis_details": analysis_details
    }

