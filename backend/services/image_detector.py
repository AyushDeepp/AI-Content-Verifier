import httpx
import google.generativeai as genai
from typing import Dict, Any, Optional, List
from core.config import settings
import logging
import asyncio
import base64
from io import BytesIO
from PIL import Image
from huggingface_hub import InferenceClient
import json
import re

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

# --- ENGINE 2: GEMINI VISION FORENSICS ---

async def get_gemini_vision_forensics(image_data: bytes) -> Dict[str, Any]:
    """Uses Gemini Vision to identify specific AI artifacts in an image"""
    if not hasattr(settings, 'GEMINI_API_KEY') or not settings.GEMINI_API_KEY:
        return None
        
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
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
        # Fallback logic for quota management
        model_names = ['gemini-2.5-flash', 'gemini-3.1-flash-lite-preview']
        response = None
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = await asyncio.to_thread(model.generate_content, [prompt, image])
                if response:
                    logger.info(f"GEMINI VISION ENGINE: Success using {model_name}")
                    break
            except Exception as e:
                logger.warning(f"Gemini {model_name} unavailable: {e}")
                continue
        
        if not response:
            return None
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except Exception as e:
        logger.error(f"Gemini vision forensics failed: {e}")
    return None

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
    
    hf_results = await asyncio.gather(*hf_tasks)
    gemini_result = await gemini_task
    
    valid_hf_scores = [s for s in hf_results if s is not None]
    hf_score = sum(valid_hf_scores) / len(valid_hf_scores) if valid_hf_scores else None
    
    # --- WEIGHTED ENSEMBLE ---
    
    # Weights: HF (60%), Gemini (40%)
    ensemble_ai_score = 0.0
    total_active_weight = 0.0
    
    # Bayesian Weights by Reliability
    # Neural (60%), Gemini Vision (40%)
    weights = {"hf": 0.6, "gemini": 0.4}
    
    numerator = 0.0
    denominator = 0.0
    
    if hf_score is not None:
        # Neural models are good at frequency noise, but can miss clean logos
        hf_conf = 0.7 
        numerator += hf_score * hf_conf * weights["hf"]
        denominator += hf_conf * weights["hf"]
        
    if gemini_result:
        g_verdict = gemini_result["verdict"]
        g_conf = gemini_result["confidence"]
        g_score = gemini_result.get("score_ai", g_conf if g_verdict == "AI-Generated" else (1.0 - g_conf))
        
        # Penalize Gemini if it says "Human" but HF says "AI" (Neural noise is more reliable than Gemini's style guess for images)
        g_reliability = g_conf
        if g_verdict == "Human-Created" and hf_score is not None and hf_score > 0.8:
            logger.warning("Neural noise detected AI, but Gemini style guess said Human. Reducing Gemini weight.")
            g_reliability *= 0.5
            
        numerator += g_score * g_reliability * weights["gemini"]
        denominator += g_reliability * weights["gemini"]
        
    final_ai_score = numerator / denominator if denominator > 0 else 0.5
    
    logger.info(f"IMAGE FORENSIC ENSEMBLE: Score={final_ai_score:.2f}, Reliability={denominator:.2f}")
    
    is_ai = final_ai_score > 0.5
    confidence = final_ai_score if is_ai else (1.0 - final_ai_score)
    
    # Build detailed analysis
    analysis_details = []
    if hf_score is not None:
        analysis_details.append({
            "model": "Vision Transformer (ViT) Classifier",
            "verdict": "AI-Generated" if hf_score > 0.5 else "Human-Created",
            "confidence": f"{int(max(hf_score, 1-hf_score)*100)}%",
            "analysis": "Analyzed pixel-level frequency components and GAN artifacts."
        })
        
    if gemini_result:
        anoms = gemini_result.get("anomalies", [])
        analysis_details.append({
            "model": "Forensic Vision Auditor",
            "verdict": gemini_result["verdict"],
            "confidence": f"{int(gemini_result['confidence']*100)}%",
            "analysis": f"Anomalies detected: {', '.join(anoms) if anoms else 'No specific structural anomalies found.'}"
        })
        
    return {
        "result": is_ai,
        "confidence": float(confidence),
        "ai_score": float(final_ai_score),
        "real_score": float(1.0 - final_ai_score),
        "method": "Multi-Engine Ensemble",
        "analysis_details": analysis_details
    }

