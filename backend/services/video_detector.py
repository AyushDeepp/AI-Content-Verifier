from typing import Dict, Any, List
import logging
import cv2
import numpy as np
from io import BytesIO
import tempfile
import os
from services.image_detector import detect_ai_image

logger = logging.getLogger(__name__)


async def extract_frames(video_data: bytes, num_frames: int = 5) -> List[bytes]:
    """
    Extract frames from video for analysis
    Returns list of frame images as bytes
    Supports multiple video formats (mp4, avi, mov, webm, etc.)
    """
    frames = []
    temp_video_path = None
    
    try:
        # Determine video format from magic bytes or use default
        video_suffix = '.mp4'  # Default
        if video_data[:4] == b'RIFF':
            video_suffix = '.avi'
        elif video_data[:4] == b'ftyp':
            if b'mp4' in video_data[:20] or b'isom' in video_data[:20]:
                video_suffix = '.mp4'
            elif b'qt' in video_data[:20]:
                video_suffix = '.mov'
        elif video_data[:4] == b'\x1a\x45\xdf\xa3':
            video_suffix = '.webm'
        
        # Save video data to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=video_suffix) as temp_video:
            temp_video.write(video_data)
            temp_video_path = temp_video.name
        
        try:
            # Open video with OpenCV
            cap = cv2.VideoCapture(temp_video_path)
            
            if not cap.isOpened():
                logger.error(f"Failed to open video file: {temp_video_path}")
                return frames
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 1.0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            logger.info(f"Video properties: {total_frames} frames, {fps:.2f} fps, {width}x{height}")
            
            if total_frames <= 0:
                logger.error("Video has no frames or invalid frame count")
                return frames
            
            # Calculate frame indices to extract (evenly distributed)
            num_frames_to_extract = min(num_frames, total_frames)
            frame_indices = np.linspace(0, total_frames - 1, num_frames_to_extract, dtype=int)
            
            # Extract frames
            frames_extracted = 0
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret and frame is not None:
                    # Handle grayscale or color images
                    if len(frame.shape) == 2:
                        # Grayscale - convert to RGB
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
                    elif len(frame.shape) == 3:
                        # BGR to RGB
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    else:
                        logger.warning(f"Unexpected frame shape: {frame.shape}")
                        continue
                    
                    # Resize if too large (max 1024px on longest side)
                    max_size = 1024
                    h, w = frame_rgb.shape[:2]
                    if max(h, w) > max_size:
                        ratio = max_size / max(h, w)
                        new_w = int(w * ratio)
                        new_h = int(h * ratio)
                        frame_rgb = cv2.resize(frame_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
                    
                    # Encode as JPEG
                    _, buffer = cv2.imencode('.jpg', frame_rgb, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    if buffer is not None:
                        frame_bytes = buffer.tobytes()
                        frames.append(frame_bytes)
                        frames_extracted += 1
                        logger.debug(f"Extracted frame {frame_idx}/{total_frames}")
                else:
                    logger.warning(f"Failed to read frame {frame_idx}")
            
            cap.release()
            logger.info(f"Successfully extracted {frames_extracted} frames from video")
            
        finally:
            # Clean up temporary file
            if temp_video_path and os.path.exists(temp_video_path):
                try:
                    os.unlink(temp_video_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file: {e}")
    
    except Exception as e:
        logger.error(f"Error extracting frames: {e}", exc_info=True)
    
    return frames


async def detect_ai_video(video_data: bytes) -> Dict[str, Any]:
    """
    Detect if video is AI-generated using frame extraction and image analysis
    Extracts frames from video and analyzes them using image detection models
    """
    if not video_data or len(video_data) == 0:
        return {
            "result": False,
            "confidence": 0.5,
            "ai_score": 0.5,
            "real_score": 0.5,
            "error": "Video data cannot be empty"
        }
    
    try:
        logger.info("Starting video analysis...")
        
        # Extract frames from video (5-10 frames for analysis)
        frames = await extract_frames(video_data, num_frames=8)
        
        if len(frames) == 0:
            logger.error("Failed to extract frames from video")
            return {
                "result": False,
                "confidence": 0.5,
                "ai_score": 0.5,
                "real_score": 0.5,
                "error": "Failed to extract frames from video"
            }
        
        logger.info(f"Extracted {len(frames)} frames for analysis")
        
        # Analyze each frame
        frame_results = []
        ai_scores = []
        real_scores = []
        
        for i, frame in enumerate(frames):
            try:
                logger.debug(f"Analyzing frame {i+1}/{len(frames)}...")
                frame_result = await detect_ai_image(frame)
                
                if "ai_score" in frame_result and "real_score" in frame_result:
                    ai_scores.append(frame_result["ai_score"])
                    real_scores.append(frame_result["real_score"])
                    frame_results.append(frame_result)
                
            except Exception as e:
                logger.error(f"Error analyzing frame {i+1}: {e}")
                continue
        
        if len(ai_scores) == 0:
            logger.error("Failed to analyze any frames")
            return {
                "result": False,
                "confidence": 0.5,
                "ai_score": 0.5,
                "real_score": 0.5,
                "error": "Failed to analyze video frames"
            }
        
        # Aggregate results from all frames
        # Use average of all frame scores
        avg_ai_score = np.mean(ai_scores)
        avg_real_score = np.mean(real_scores)
        
        # Normalize scores
        total = avg_ai_score + avg_real_score
        if total > 0:
            avg_ai_score = avg_ai_score / total
            avg_real_score = avg_real_score / total
        
        # Determine if video is AI-generated
        is_ai_generated = avg_ai_score > avg_real_score
        confidence = avg_ai_score if is_ai_generated else avg_real_score
        
        # Additional heuristics based on consistency
        # If most frames agree, increase confidence
        ai_frame_count = sum(1 for r in frame_results if r.get("result", False))
        consistency = abs(ai_frame_count - (len(frame_results) - ai_frame_count)) / len(frame_results)
        
        # Boost confidence if frames are consistent
        if consistency > 0.6:
            confidence = min(1.0, confidence * 1.1)
        
        logger.info(f"Video analysis complete: AI={avg_ai_score:.2f}, Real={avg_real_score:.2f}, "
                   f"Frames analyzed={len(frame_results)}")
        
        return {
            "result": is_ai_generated,
            "confidence": float(confidence),
            "ai_score": float(avg_ai_score),
            "real_score": float(avg_real_score),
            "frames_analyzed": len(frame_results),
            "total_frames": len(frames),
            "method": "frame_extraction"
        }
        
    except Exception as e:
        logger.error(f"Error in video detection: {e}", exc_info=True)
        return {
            "result": False,
            "confidence": 0.5,
            "ai_score": 0.5,
            "real_score": 0.5,
            "error": f"Error processing video: {str(e)}"
        }


