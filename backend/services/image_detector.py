import httpx
from typing import Dict, Any
from core.config import settings
import logging
import asyncio
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

# Multiple models for better reliability
IMAGE_MODELS = [
    "orvit/gan-image-detection",
    "Falconsai/nsfw_image_detection",  # Alternative model
    "sentence-transformers/clip-vit-base-patch32"  # For feature extraction if needed
]


async def detect_ai_image(image_data: bytes) -> Dict[str, Any]:
    """
    Detect if image is AI-generated using Hugging Face API
    Tries multiple models for better reliability
    """
    if not image_data or len(image_data) == 0:
        return {
            "result": False,
            "confidence": 0.5,
            "ai_score": 0.5,
            "real_score": 0.5,
            "error": "Image data cannot be empty"
        }
    
    # Validate image format
    try:
        image = Image.open(BytesIO(image_data))
        image.verify()  # Verify it's a valid image
        # Reset file pointer after verify
        image = Image.open(BytesIO(image_data))
        
        # Resize if too large (max 1024px on longest side)
        max_size = 1024
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            # Convert back to bytes
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
    
    async with httpx.AsyncClient(timeout=90.0) as client:
        for model_name in IMAGE_MODELS[:1]:  # Use primary model for now
            try:
                api_url = f"https://api-inference.huggingface.co/models/{model_name}"
                headers = {
                    "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"
                }
                
                # Make request with image data
                response = await client.post(api_url, headers=headers, content=image_data)
                
                # Handle model loading (503 status)
                if response.status_code == 503:
                    retry_after = int(response.headers.get("Retry-After", 30))
                    logger.info(f"Model {model_name} is loading, waiting {retry_after}s...")
                    await asyncio.sleep(retry_after)
                    
                    # Retry once
                    response = await client.post(api_url, headers=headers, content=image_data)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Parse the result - handle different formats
                    predictions = None
                    if isinstance(result, list):
                        if len(result) > 0:
                            if isinstance(result[0], list):
                                predictions = result[0]
                            else:
                                predictions = result
                    elif isinstance(result, dict):
                        if "label" in result and "score" in result:
                            predictions = [result]
                    
                    if predictions:
                        ai_score = 0.0
                        real_score = 0.0
                        
                        for pred in predictions:
                            label = pred.get("label", "").lower()
                            score = pred.get("score", 0.0)
                            
                            # Check various label patterns
                            if any(keyword in label for keyword in ["fake", "ai", "gan", "generated", "synthetic", "artificial"]):
                                ai_score = max(ai_score, score)
                            elif any(keyword in label for keyword in ["real", "natural", "authentic", "original", "human"]):
                                real_score = max(real_score, score)
                        
                        # If we have scores, use them
                        if ai_score > 0 or real_score > 0:
                            # Normalize if needed
                            total = ai_score + real_score
                            if total > 1.0:
                                ai_score = ai_score / total
                                real_score = real_score / total
                            elif total < 0.1:
                                # Fallback if scores are too low
                                ai_score = 0.5
                                real_score = 0.5
                            
                            # If still no clear scores, use first prediction
                            if ai_score == 0.0 and real_score == 0.0 and len(predictions) > 0:
                                first_pred = predictions[0]
                                label = first_pred.get("label", "").lower()
                                score = first_pred.get("score", 0.0)
                                # Heuristic: if label contains certain keywords, assume AI
                                if any(keyword in label for keyword in ["fake", "ai", "gan"]):
                                    ai_score = score
                                    real_score = 1.0 - score
                                else:
                                    real_score = score
                                    ai_score = 1.0 - score
                            
                            is_ai_generated = ai_score > real_score
                            confidence = ai_score if is_ai_generated else real_score
                            
                            logger.info(f"Image detection successful with {model_name}: AI={ai_score:.2f}, Real={real_score:.2f}")
                            
                            return {
                                "result": is_ai_generated,
                                "confidence": float(confidence),
                                "ai_score": float(ai_score),
                                "real_score": float(real_score),
                                "model": model_name
                            }
                
                # If we get here, the model didn't work as expected
                logger.warning(f"Model {model_name} returned unexpected format: {response.status_code}")
                
            except httpx.TimeoutException:
                logger.warning(f"Timeout calling {model_name}, trying next model...")
                continue
            except Exception as e:
                logger.error(f"Error with model {model_name}: {e}")
                continue
    
    # All models failed, return fallback
    logger.error("All image detection models failed")
    return {
        "result": False,
        "confidence": 0.5,
        "ai_score": 0.5,
        "real_score": 0.5,
        "error": "All models failed to process the image"
    }

