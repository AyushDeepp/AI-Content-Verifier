import httpx
import google.generativeai as genai
from typing import Dict, Any
from core.config import settings
import logging
import asyncio
import base64
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)


async def detect_with_gemini(image_data: bytes, content_type: str = "image") -> Dict[str, Any]:
    """
    Use Google Gemini API to detect if image/video is AI-generated
    Specifically good at detecting Google AI (Imagen, etc.)
    """
    if not hasattr(settings, 'GEMINI_API_KEY') or not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not configured")
        return None
    
    try:
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Use the latest Gemini 2.0 Flash model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Prepare image
        image = Image.open(BytesIO(image_data))
        
        # Create prompt for AI detection
        prompt = """You are a Digital Content Forensic Expert. Your task is to determine if the provided media is AI-generated.

### PHASE 1: Metadata & Digital Markers
Search the provided file's context (if available) for any metadata indicators or known Google SynthID signatures. Note: As an AI model, you are looking for known patterns associated with Google Imagen, Veo, or Gemini generations.

### PHASE 2: Visual Artifact Analysis
Analyze the content for the following:
1. ANATOMICAL ERRORS: Check fingers, eyes, and limb joints.
2. TEXTURE INCONSISTENCIES: Look for 'waxy' skin, blurred background objects, or nonsensical text.
3. PHYSICS: Check for floating objects or shadows that don't align with light sources.
4. Signs of diffusion model artifacts
5. Text that looks garbled or incorrect

OUTPUT FORMAT:
    1. VERDICT: [AI-Generated / Human-Created / Uncertain]
    2. CONFIDENCE: [X/100]
    3. REASON: [Brief explanation of the specific markers found]
"""
        
        # Generate response
        response = model.generate_content([prompt, image])
        response_text = response.text
        
        logger.info(f"Gemini response: {response_text}")
        
        # Parse response - handle new format
        try:
            # Extract verdict
            ai_generated = False
            human_created = False
            
            if "VERDICT:" in response_text or "VERDICT" in response_text:
                verdict_line = [line for line in response_text.split('\n') if 'VERDICT' in line.upper()][0]
                logger.info(f"Verdict line: {verdict_line}")
                
                # Check what's inside the brackets [...]
                import re
                bracket_match = re.search(r'\[(.*?)\]', verdict_line)
                if bracket_match:
                    verdict_content = bracket_match.group(1).upper()
                    logger.info(f"Verdict content: {verdict_content}")
                    
                    ai_generated = any(keyword in verdict_content for keyword in ["AI-GENERATED", "AI GENERATED", "ARTIFICIAL"])
                    human_created = any(keyword in verdict_content for keyword in ["HUMAN-CREATED", "HUMAN CREATED", "HUMAN", "REAL"])
                else:
                    # Fallback: check the line
                    ai_generated = any(keyword in verdict_line.upper() for keyword in ["AI-GENERATED", "AI GENERATED"])
                    human_created = any(keyword in verdict_line.upper() for keyword in ["HUMAN-CREATED", "HUMAN CREATED"])
            else:
                # Fallback: check entire response
                ai_generated = any(keyword in response_text.upper() for keyword in ["AI-GENERATED", "AI GENERATED", "ARTIFICIAL INTELLIGENCE"])
                human_created = any(keyword in response_text.upper() for keyword in ["HUMAN-CREATED", "HUMAN CREATED", "REAL PHOTOGRAPH"])
            
            logger.info(f"Parsed verdict: ai_generated={ai_generated}, human_created={human_created}")
            
            # Extract confidence
            confidence = 0.7  # Default
            try:
                confidence_line = [line for line in response_text.split('\n') if 'CONFIDENCE' in line.upper()][0]
                logger.info(f"Confidence line: {confidence_line}")
                
                # Extract number from formats like "90/100" or "90" inside brackets
                import re
                # First try to find number inside brackets [90/100] or [90]
                bracket_match = re.search(r'\[(\d+)', confidence_line)
                if bracket_match:
                    conf_value = int(bracket_match.group(1))
                    confidence = conf_value / 100.0 if conf_value > 1 else conf_value
                    logger.info(f"Extracted confidence from brackets: {conf_value} -> {confidence}")
                else:
                    # Fallback: find any number
                    numbers = re.findall(r'\d+', confidence_line)
                    if numbers:
                        conf_value = int(numbers[0])
                        confidence = conf_value / 100.0 if conf_value > 1 else conf_value
                        logger.info(f"Extracted confidence from line: {conf_value} -> {confidence}")
            except Exception as e:
                logger.warning(f"Could not parse confidence: {e}, using default")
            
            # Determine AI score based on verdict
            # IMPORTANT: confidence represents how sure we are of the verdict
            logger.info(f"Before calculation: ai_generated={ai_generated}, human_created={human_created}, confidence={confidence}")
            
            if ai_generated and not human_created:
                # Verdict is AI-Generated, so AI score = confidence
                ai_score = round(confidence, 2)
                real_score = round(1.0 - confidence, 2)
                logger.info(f"AI-Generated branch: ai_score={ai_score}, real_score={real_score}")
            elif human_created and not ai_generated:
                # Verdict is Human-Created, so real score = confidence
                ai_score = round(1.0 - confidence, 2)
                real_score = round(confidence, 2)
                logger.info(f"Human-Created branch: ai_score={ai_score}, real_score={real_score}")
            else:
                # Uncertain or both - use 50/50
                ai_score = 0.5
                real_score = 0.5
                confidence = 0.5
                logger.info(f"Uncertain branch: ai_score={ai_score}, real_score={real_score}")
            
            # Extract reason
            reason = ""
            try:
                if "REASON:" in response_text:
                    # Find the REASON: line and get everything after it
                    reason_parts = response_text.split("REASON:")
                    if len(reason_parts) > 1:
                        # Get everything after REASON: and clean it up
                        reason = reason_parts[1].strip()
                        # Remove any leading numbering like "3. "
                        reason = re.sub(r'^\d+\.\s*', '', reason)
                        logger.info(f"Extracted reason: {reason[:100]}...")
                elif "3." in response_text and "REASON" in response_text.upper():
                    # Handle numbered format
                    lines = response_text.split('\n')
                    reason_started = False
                    reason_lines = []
                    for line in lines:
                        if 'REASON' in line.upper():
                            reason_started = True
                            # Remove the "3. REASON:" part
                            clean_line = re.sub(r'^\d+\.\s*REASON:\s*', '', line, flags=re.IGNORECASE)
                            if clean_line.strip():
                                reason_lines.append(clean_line.strip())
                        elif reason_started and line.strip():
                            # Continue collecting reason lines
                            reason_lines.append(line.strip())
                    reason = ' '.join(reason_lines)
                    logger.info(f"Extracted reason (numbered): {reason[:100]}...")
            except Exception as e:
                logger.warning(f"Could not parse reason: {e}")
            
            logger.info(f"Gemini detection: AI={ai_score:.2f}, Real={real_score:.2f}")
            
            return {
                "ai_score": float(ai_score),
                "real_score": float(real_score),
                "confidence": float(confidence),
                "model": "gemini-2.0-flash-exp",
                "reason": reason if reason else "Analysis completed"
            }
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return None
        
    except Exception as e:
        logger.error(f"Error with Gemini API: {e}")
        return None


async def detect_with_huggingface(image_data: bytes) -> Dict[str, Any]:
    """
    Use Hugging Face models for image detection
    NOTE: Currently all HF image models are deprecated (410 Gone)
    This function is kept for future when working models are available
    """
    # All models are currently deprecated, skip to save time
    logger.info("Skipping Hugging Face models (all deprecated)")
    return None


async def detect_ai_image(image_data: bytes) -> Dict[str, Any]:
    """
    Enhanced image detection using multiple methods (ensemble)
    """
    if not image_data or len(image_data) == 0:
        return {
            "result": False,
            "confidence": 0.5,
            "ai_score": 0.5,
            "real_score": 0.5,
            "error": "Image data cannot be empty"
        }
    
    # Validate and resize image
    try:
        image = Image.open(BytesIO(image_data))
        image.verify()
        image = Image.open(BytesIO(image_data))
        
        max_size = 1024
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            output = BytesIO()
            image.save(output, format=image.format or 'JPEG', quality=85)
            image_data = output.getvalue()
            logger.info(f"Image resized to {new_size}")
    except Exception as e:
        logger.error(f"Invalid image format: {e}")
        return {
            "result": False,
            "confidence": 0.5,
            "ai_score": 0.5,
            "real_score": 0.5,
            "error": "Invalid image format"
        }
    
    # Collect results from different methods
    results = []
    analysis_details = []
    
    # Try Gemini API
    gemini_result = await detect_with_gemini(image_data)
    if gemini_result:
        results.append(gemini_result)
        if "reason" in gemini_result and gemini_result["reason"]:
            analysis_details.append({
                "model": "Gemini 2.0 Flash",
                "verdict": "AI-Generated" if gemini_result["ai_score"] > 0.5 else "Real/Human",
                "confidence": f"{gemini_result['confidence']*100:.0f}%",
                "analysis": gemini_result["reason"]
            })
    
    # Try Hugging Face
    hf_result = await detect_with_huggingface(image_data)
    if hf_result:
        results.append(hf_result)
        analysis_details.append({
            "model": hf_result.get("model", "Hugging Face"),
            "verdict": "AI-Generated" if hf_result["ai_score"] > 0.5 else "Real/Human",
            "confidence": f"{max(hf_result['ai_score'], hf_result['real_score'])*100:.0f}%"
        })
    
    # If we have results, use ensemble
    if len(results) > 0:
        avg_ai_score = sum(r["ai_score"] for r in results) / len(results)
        avg_real_score = sum(r["real_score"] for r in results) / len(results)
        
        is_ai_generated = avg_ai_score > avg_real_score
        confidence = avg_ai_score if is_ai_generated else avg_real_score
        
        # Boost confidence if models agree
        agreement_count = sum(1 for r in results if (r["ai_score"] > r["real_score"]) == is_ai_generated)
        agreement_ratio = agreement_count / len(results)
        
        if agreement_ratio >= 0.8:
            confidence = min(1.0, confidence * 1.1)
        
        logger.info(f"Image ensemble: AI={avg_ai_score:.2f}, Real={avg_real_score:.2f}, "
                   f"Models={len(results)}, Agreement={agreement_ratio:.0%}")
        
        return {
            "result": is_ai_generated,
            "confidence": float(confidence),
            "ai_score": float(avg_ai_score),
            "real_score": float(avg_real_score),
            "models_used": len(results),
            "method": "ensemble",
            "analysis_details": analysis_details  # Include detailed analysis
        }
    
    # Fallback
    logger.warning("All image detection methods failed")
    return {
        "result": False,
        "confidence": 0.5,
        "ai_score": 0.5,
        "real_score": 0.5,
        "error": "All detection methods failed"
    }

