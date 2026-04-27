import google.generativeai as genai
from typing import Dict, Any
from core.config import settings
import logging
import tempfile
import os
import cv2
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)


async def detect_ai_video(video_data: bytes) -> Dict[str, Any]:
    """
    Detect if video is AI-generated using Gemini API
    Analyzes representative frames from the video
    """
    if not video_data or len(video_data) == 0:
        return {
            "result": False,
            "confidence": 0.5,
            "ai_score": 0.5,
            "real_score": 0.5,
            "error": "Video data cannot be empty"
        }
    
    # Check if Gemini API key is configured
    if not hasattr(settings, 'GEMINI_API_KEY') or not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not configured")
        return {
            "result": False,
            "confidence": 0.5,
            "ai_score": 0.5,
            "real_score": 0.5,
            "error": "Gemini API key not configured"
        }
    
    temp_video_path = None
    
    try:
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Save video to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
            temp_video.write(video_data)
            temp_video_path = temp_video.name
        
        logger.info(f"Analyzing video with Gemini ({len(video_data)} bytes)...")
        
        # Extract 3 representative frames (beginning, middle, end)
        cap = cv2.VideoCapture(temp_video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frames_to_analyze = [
            total_frames // 4,      # 25%
            total_frames // 2,      # 50%
            3 * total_frames // 4   # 75%
        ]
        
        frame_images = []
        for frame_pos in frames_to_analyze:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            ret, frame = cap.read()
            if ret:
                _, buffer = cv2.imencode('.jpg', frame)
                frame_image = Image.open(BytesIO(buffer.tobytes()))
                frame_images.append(frame_image)
        
        cap.release()
        
        if not frame_images:
            raise Exception("Could not extract frames from video")
        
        logger.info(f"Extracted {len(frame_images)} frames for analysis")
        
        # Create prompt for video analysis
        prompt = """You are analyzing frames from a VIDEO to determine if it's AI-generated.

### IMPORTANT: This is VIDEO content, not just images
Look for VIDEO-specific indicators:
1. **Temporal Artifacts**: Motion blur inconsistencies, unnatural frame transitions
2. **AI Video Watermarks**: Veo, Sora, Runway, Pika, etc.
3. **Consistency Across Frames**: Do objects/people maintain consistency?
4. **Motion Patterns**: Unnatural movement, physics violations
5. **Standard AI Indicators**: Garbled text, anatomical errors, waxy textures

OUTPUT FORMAT:
1. VERDICT: [AI-Generated / Human-Created / Uncertain]
2. CONFIDENCE: [X/100]
3. REASON: [Detailed explanation focusing on VIDEO-specific markers]
"""
        
        # Analyze with Gemini
        logger.info("Sending frames to Gemini for analysis...")
        response = model.generate_content([prompt] + frame_images)
        response_text = response.text
        
        logger.info(f"Gemini video response: {response_text}")
        
        # Parse response (same logic as image detection)
        import re
        
        ai_generated = False
        human_created = False
        
        if "VERDICT:" in response_text or "VERDICT" in response_text:
            verdict_line = [line for line in response_text.split('\n') if 'VERDICT' in line.upper()][0]
            logger.info(f"Verdict line: {verdict_line}")
            
            # Try to extract from brackets first [AI-Generated]
            bracket_match = re.search(r'\[(.*?)\]', verdict_line)
            if bracket_match:
                verdict_content = bracket_match.group(1).upper()
                logger.info(f"Verdict content (bracketed): {verdict_content}")
            else:
                # No brackets, extract text after "VERDICT:" or "VERDICT"
                if ':' in verdict_line:
                    verdict_content = verdict_line.split(':', 1)[1].strip().upper()
                else:
                    verdict_content = verdict_line.replace('VERDICT', '', 1).strip().upper()
                logger.info(f"Verdict content (non-bracketed): {verdict_content}")
            
            ai_generated = any(keyword in verdict_content for keyword in ["AI-GENERATED", "AI GENERATED", "ARTIFICIAL"])
            human_created = any(keyword in verdict_content for keyword in ["HUMAN-CREATED", "HUMAN CREATED", "HUMAN", "REAL"])
        else:
            logger.warning("No VERDICT found in response")
        
        logger.info(f"Parsed verdict: ai_generated={ai_generated}, human_created={human_created}")
        
        # Extract confidence
        confidence = 0.7
        try:
            confidence_line = [line for line in response_text.split('\n') if 'CONFIDENCE' in line.upper()][0]
            logger.info(f"Confidence line: {confidence_line}")
            
            # Try brackets first [95/100] or [95]
            bracket_match = re.search(r'\[(\d+)', confidence_line)
            if bracket_match:
                conf_value = int(bracket_match.group(1))
                confidence = conf_value / 100.0 if conf_value > 1 else conf_value
                logger.info(f"Extracted confidence (bracketed): {confidence}")
            else:
                # No brackets, extract number after "CONFIDENCE:" like "95/100" or "95"
                # Remove "CONFIDENCE:" and extract first number
                conf_text = confidence_line.split(':', 1)[1] if ':' in confidence_line else confidence_line
                numbers = re.findall(r'\d+', conf_text)
                if numbers:
                    conf_value = int(numbers[0])
                    confidence = conf_value / 100.0 if conf_value > 1 else conf_value
                    logger.info(f"Extracted confidence (non-bracketed): {confidence}")
        except Exception as e:
            logger.warning(f"Could not parse confidence: {e}")
        
        # Calculate scores
        if ai_generated and not human_created:
            ai_score = round(confidence, 2)
            real_score = round(1.0 - confidence, 2)
        elif human_created and not ai_generated:
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
            else:
                logger.warning("No REASON found in response")
        except Exception as e:
            logger.warning(f"Could not parse reason: {e}")
        
        logger.info(f"Video analysis: AI={ai_score}, Real={real_score}, Reason length={len(reason)}")
        
        # Build response with analysis details
        result = {
            "result": bool(ai_score > real_score),
            "confidence": float(max(ai_score, real_score)),
            "ai_score": float(ai_score),
            "real_score": float(real_score),
            "frames_analyzed": len(frame_images),
            "method": "gemini_video_frames"
        }
        
        # Add analysis details if reason exists
        if reason:
            result["analysis_details"] = [{
                "model": "Gemini 2.0 Flash (Video)",
                "verdict": "AI-Generated" if ai_score > real_score else "Human-Created",
                "confidence": f"{int(confidence*100)}%",
                "analysis": reason
            }]
        
        return result
        
    except Exception as e:
        logger.error(f"Error with Gemini video analysis: {e}", exc_info=True)
        return {
            "result": False,
            "confidence": 0.5,
            "ai_score": 0.5,
            "real_score": 0.5,
            "error": f"Video analysis failed: {str(e)}"
        }
    
    finally:
        # Clean up temporary file
        if temp_video_path and os.path.exists(temp_video_path):
            try:
                os.unlink(temp_video_path)
            except:
                pass