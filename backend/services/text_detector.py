from typing import Dict, Any
import logging
import re
from core.config import settings

logger = logging.getLogger(__name__)

# NOTE: Hugging Face Inference API (api-inference.huggingface.co) is deprecated (410 Gone)
# Using Gemini API as primary method with heuristic fallback


def heuristic_text_analysis(text: str) -> Dict[str, Any]:
    """
    Fallback heuristic analysis when API is unavailable
    """
    # Simple pattern-based analysis
    ai_indicators = [
        r'\b(furthermore|moreover|additionally|consequently)\b',
        r'\b(it is important to note|it should be noted)\b',
        r'\b(in conclusion|to summarize|in summary)\b',
        r'\b(various|numerous|multitude)\b',
        r'\b(utilize|leverage|facilitate)\b',
    ]
    
    ai_score = 0.0
    for pattern in ai_indicators:
        if re.search(pattern, text, re.IGNORECASE):
            ai_score += 0.15
    
    # Check for overly perfect grammar (no contractions, no informal language)
    if "'" not in text and len(text) > 100:
        ai_score += 0.1
    
    # Normalize
    ai_score = min(ai_score, 0.9)
    human_score = 1.0 - ai_score
    
    logger.info(f"Heuristic analysis: AI={ai_score:.2f}, Human={human_score:.2f}, Confidence={max(ai_score, human_score):.2f}")
    
    return {
        "is_ai_generated": ai_score > 0.5,
        "confidence": max(ai_score, human_score),
        "ai_score": ai_score,
        "human_score": human_score
    }


async def detect_with_gemini(text: str) -> Dict[str, Any]:
    """
    Use Gemini API for text detection (fallback)
    """
    if not hasattr(settings, 'GEMINI_API_KEY') or not settings.GEMINI_API_KEY:
        return None
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""Analyze this text to determine if it's AI-generated or human-written.

TEXT TO ANALYZE:
{text[:2000]}

ANALYSIS CRITERIA:
1. **Writing Style**: Check for overly formal, repetitive, or generic phrasing
2. **Sentence Structure**: Look for unnatural uniformity or perfect grammar
3. **Content Patterns**: Identify AI-typical patterns (lists, structured responses, hedging language)
4. **Authenticity**: Assess natural flow, personal voice, and human imperfections

OUTPUT FORMAT:
1. VERDICT: AI-Generated / Human-Written
2. CONFIDENCE: X/100
3. REASON: Brief explanation of key indicators
"""
        
        response = model.generate_content(prompt)
        response_text = response.text
        
        logger.info(f"Gemini text analysis complete")
        
        # Parse response
        ai_generated = False
        human_written = False
        
        if "VERDICT:" in response_text or "VERDICT" in response_text:
            verdict_line = [line for line in response_text.split('\n') if 'VERDICT' in line.upper()][0]
            
            # Try brackets first
            bracket_match = re.search(r'\[(.*?)\]', verdict_line)
            if bracket_match:
                verdict_content = bracket_match.group(1).upper()
            else:
                # No brackets
                verdict_content = verdict_line.split(':', 1)[1].strip().upper() if ':' in verdict_line else verdict_line.replace('VERDICT', '', 1).strip().upper()
            
            ai_generated = any(keyword in verdict_content for keyword in ["AI-GENERATED", "AI GENERATED", "ARTIFICIAL"])
            human_written = any(keyword in verdict_content for keyword in ["HUMAN-WRITTEN", "HUMAN WRITTEN", "HUMAN", "REAL"])
        
        # Extract confidence
        confidence = 0.7
        try:
            confidence_line = [line for line in response_text.split('\n') if 'CONFIDENCE' in line.upper()][0]
            bracket_match = re.search(r'\[(\d+)', confidence_line)
            if bracket_match:
                conf_value = int(bracket_match.group(1))
            else:
                conf_text = confidence_line.split(':', 1)[1] if ':' in confidence_line else confidence_line
                numbers = re.findall(r'\d+', conf_text)
                conf_value = int(numbers[0]) if numbers else 70
            confidence = conf_value / 100.0 if conf_value > 1 else conf_value
        except:
            pass
        
        # Calculate scores
        if ai_generated and not human_written:
            ai_score = round(confidence, 2)
            real_score = round(1.0 - confidence, 2)
        elif human_written and not ai_generated:
            ai_score = round(1.0 - confidence, 2)
            real_score = round(confidence, 2)
        else:
            ai_score = 0.5
            real_score = 0.5
        
        # Extract reason
        reason = ""
        try:
            if "REASON:" in response_text:
                reason_parts = response_text.split("REASON:")
                if len(reason_parts) > 1:
                    reason = reason_parts[1].strip()
                    # Remove leading number like "3. "
                    reason = re.sub(r'^\d+\.\s*', '', reason)
                    logger.info(f"Extracted reason: {reason[:100]}...")
        except Exception as e:
            logger.warning(f"Could not parse reason: {e}")
        
        logger.info(f"Gemini text detection: AI={ai_score}, Real={real_score}")
        
        result = {
            "ai_score": float(ai_score),
            "real_score": float(real_score),
            "confidence": float(confidence)
        }
        
        # Add analysis details if reason exists
        if reason:
            result["analysis_details"] = [{
                "model": "Gemini 2.0 Flash (Text)",
                "verdict": "AI-Generated" if ai_score > real_score else "Human-Written",
                "confidence": f"{int(confidence*100)}%",
                "analysis": reason
            }]
        
        return result
        
    except Exception as e:
        logger.error(f"Error with Gemini text detection: {e}")
        return None


async def detect_ai_text(text: str) -> Dict[str, Any]:
    """
    Main function to detect if text is AI-generated
    Uses Gemini API as primary method with heuristic fallback
    
    NOTE: Hugging Face Inference API is deprecated (returns 410 Gone)
    """
    if not text or len(text.strip()) < 10:
        return {
            "result": False,
            "confidence": 0.5,
            "error": "Text too short to analyze"
        }
    
    # Try Gemini
    logger.info("Using Gemini for text detection...")
    gemini_result = await detect_with_gemini(text)
    
    if gemini_result:
        is_ai = gemini_result["ai_score"] > gemini_result["real_score"]
        return {
            "result": is_ai,
            "confidence": float(gemini_result["confidence"]),
            "ai_score": float(gemini_result["ai_score"]),
            "real_score": float(gemini_result["real_score"]),
            "method": "gemini"
        }
    
    # Fallback to heuristic
    logger.warning("Gemini failed, using heuristic analysis")
    heuristic_result = heuristic_text_analysis(text)
    
    return {
        "result": heuristic_result["is_ai_generated"],
        "confidence": float(heuristic_result["confidence"]),
        "ai_score": float(heuristic_result["ai_score"]),
        "real_score": float(heuristic_result["human_score"]),
        "method": "heuristic"
    }
