import httpx
from typing import Dict, Any
from core.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

# Alternative model if primary fails: "distilroberta-base-openai-detector"
TEXT_MODELS = [
    "roberta-base-openai-detector",
    "distilroberta-base-openai-detector",
    "Hello-SimpleAI/chatgpt-detector-roberta"
]


async def detect_ai_text(text: str) -> Dict[str, Any]:
    """
    Detect if text is AI-generated using Hugging Face API
    Tries multiple models for better reliability
    """
    if not text or len(text.strip()) == 0:
        return {
            "result": False,
            "confidence": 0.5,
            "ai_score": 0.5,
            "human_score": 0.5,
            "error": "Text cannot be empty"
        }
    
    # Truncate text if too long (most models have token limits)
    max_length = 5000  # Conservative limit
    if len(text) > max_length:
        text = text[:max_length]
        logger.warning(f"Text truncated to {max_length} characters")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for model_name in TEXT_MODELS:
            try:
                api_url = f"https://api-inference.huggingface.co/models/{model_name}"
                headers = {
                    "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"
                }
                
                payload = {"inputs": text}
                
                # Make request
                response = await client.post(api_url, headers=headers, json=payload)
                
                # Handle model loading (503 status)
                if response.status_code == 503:
                    # Wait for model to load
                    retry_after = int(response.headers.get("Retry-After", 30))
                    logger.info(f"Model {model_name} is loading, waiting {retry_after}s...")
                    await asyncio.sleep(retry_after)
                    
                    # Retry once
                    response = await client.post(api_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Handle different response formats
                    predictions = None
                    if isinstance(result, list):
                        if len(result) > 0:
                            # Check if it's a list of predictions
                            if isinstance(result[0], list):
                                predictions = result[0]
                            else:
                                predictions = result
                    elif isinstance(result, dict):
                        # Some models return dict with labels
                        if "label" in result and "score" in result:
                            predictions = [result]
                    
                    if predictions:
                        ai_score = 0.0
                        human_score = 0.0
                        
                        for pred in predictions:
                            label = pred.get("label", "").upper()
                            score = pred.get("score", 0.0)
                            
                            if "FAKE" in label or "AI" in label or "GENERATED" in label:
                                ai_score = max(ai_score, score)
                            elif "REAL" in label or "HUMAN" in label or "ORIGINAL" in label:
                                human_score = max(human_score, score)
                        
                        # If we have scores, use them
                        if ai_score > 0 or human_score > 0:
                            # Normalize if needed
                            total = ai_score + human_score
                            if total > 1.0:
                                ai_score = ai_score / total
                                human_score = human_score / total
                            elif total < 0.1:
                                # Fallback if scores are too low
                                ai_score = 0.5
                                human_score = 0.5
                            
                            is_ai_generated = ai_score > human_score
                            confidence = ai_score if is_ai_generated else human_score
                            
                            logger.info(f"Text detection successful with {model_name}: AI={ai_score:.2f}, Human={human_score:.2f}")
                            
                            return {
                                "result": is_ai_generated,
                                "confidence": float(confidence),
                                "ai_score": float(ai_score),
                                "human_score": float(human_score),
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
    logger.error("All text detection models failed")
    return {
        "result": False,
        "confidence": 0.5,
        "ai_score": 0.5,
        "human_score": 0.5,
        "error": "All models failed to process the text"
    }

