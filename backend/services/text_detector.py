import logging
import re
import math
import asyncio
import httpx
from typing import Dict, Any, List, Optional
from core.config import settings
from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)

# --- ENGINE 1: STATISTICAL ANALYSIS (LOCAL) ---

def calculate_text_statistics(text: str) -> Dict[str, Any]:
    """Courtroom-grade Forensic Statistical Analysis"""
    # 1. Structural Tokenization
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    words = re.findall(r'\w+', text.lower())
    
    if not sentences or not words:
        return {"stat_score": 0.5, "burstiness": 0, "entropy": 0}

    # 2. Rolling Burstiness (Local vs Global Variance)
    # Humans vary sentence lengths locally; AI is consistent globally.
    sentence_lengths = [len(s.split()) for s in sentences]
    
    # Global Burstiness
    global_mean = sum(sentence_lengths) / len(sentence_lengths)
    global_std = math.sqrt(sum((x - global_mean) ** 2 for x in sentence_lengths) / len(sentence_lengths))
    global_burst = global_std / global_mean if global_mean > 0 else 0
    
    # Paragraph-level (Rolling) Burstiness Variance
    para_bursts = []
    for para in paragraphs:
        p_sents = [s.strip() for s in re.split(r'[.!?]+', para) if s.strip()]
        if len(p_sents) > 1:
            p_lens = [len(s.split()) for s in p_sents]
            p_mean = sum(p_lens) / len(p_lens)
            p_std = math.sqrt(sum((x - p_mean) ** 2 for x in p_lens) / len(p_lens))
            para_bursts.append(p_std / p_mean if p_mean > 0 else 0)
    
    # Consistency across paragraphs (AI is very consistent)
    para_consistency = 1.0 - (sum(para_bursts) / len(para_bursts) if para_bursts else 0)

    # 3. Bigram Entropy (Conditional Probability Proxy)
    # AI word sequences are highly predictable.
    bigrams = [" ".join(words[i:i+2]) for i in range(len(words)-1)]
    bigram_counts = {}
    for b in bigrams:
        bigram_counts[b] = bigram_counts.get(b, 0) + 1
    
    b_entropy = 0
    total_bigrams = len(bigrams) if bigrams else 1
    for count in bigram_counts.values():
        p = count / total_bigrams
        b_entropy -= p * math.log2(p)
    
    # Normalize Bigram Entropy (Typically lower for AI)
    # Human bigram entropy is usually > 7.0 for 500+ words
    norm_b_entropy = min(max((b_entropy - 3.0) / 6.0, 0), 1.0)

    # 4. Syntactic Regularity & AI Anchors
    ai_anchors = ["moreover", "furthermore", "consequently", "additionally", "in conclusion", 
                  "it is important to note", "on the other hand", "overall", "specifically"]
    marker_density = sum(1 for w in ai_anchors if w in text.lower()) / (len(sentences) if sentences else 1)

    # --- FORENSIC AGGREGATION ---
    # AI indicators: Low Global Burstiness, High Para Consistency, Low Bigram Entropy, High Marker Density
    ai_score = (
        (1.0 - global_burst) * 0.25 +
        para_consistency * 0.25 +
        (1.0 - norm_b_entropy) * 0.30 +
        (min(marker_density * 3.0, 1.0)) * 0.20
    )
    
    logger.info(f"FORENSIC STATS: Global_Burst={global_burst:.2f}, Para_Consistency={para_consistency:.2f}, B_Entropy={b_entropy:.2f}")
    
    return {
        "burstiness": float(global_burst),
        "para_consistency": float(para_consistency),
        "entropy": float(b_entropy),
        "stat_score": float(ai_score)
    }

# --- ENGINE 2: HUGGING FACE CLASSIFIERS ---

async def query_hf_model(model_id: str, text: str, api_key: str) -> Optional[float]:
    """Queries a specific Hugging Face model via official InferenceClient"""
    if not api_key:
        return None
        
    try:
        client = InferenceClient(model=model_id, token=api_key)
        # Use text-classification specifically
        result = await asyncio.to_thread(client.text_classification, text[:1500])
        
        if result:
            # Sort results by score to find the top label
            ai_score = 0.0
            for item in result:
                label = item.get("label", "").upper()
                score = item.get("score", 0.0)
                if any(k in label for k in ["AI", "GENERATED", "FAKE", "LABEL_1", "MACHINE"]):
                    ai_score = score
                    break
                elif any(k in label for k in ["HUMAN", "REAL", "LABEL_0"]):
                    ai_score = 1.0 - score
                    break
            
            logger.info(f"HF ENGINE ({model_id}): Score={ai_score:.2f}")
            return ai_score
    except Exception as e:
        logger.warning(f"HF Inference Error ({model_id}): {e}")
        return None
    return None

# --- ENGINE 3: GEMINI LINGUISTIC AUDITOR ---

async def get_gemini_audit(text: str) -> Dict[str, Any]:
    """Uses Gemini to provide a detailed linguistic explanation of the text's origin"""
    if not hasattr(settings, 'GEMINI_API_KEY') or not settings.GEMINI_API_KEY:
        return None
        
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        prompt = f"""You are a Multi-Agent Forensic Verification System. Analyze the following text using 4 specialized internal agents:

AGENT 1 (Stylometric Expert): Detects syntactic rigidity, "safe" vocabulary, and over-used AI transition anchors.
AGENT 2 (Logical Auditor): Checks for "hallucinated certainty" and generic, circular reasoning typical of LLMs.
AGENT 3 (Personality Scout): Looks for "Lived Experience" vs "Stochastic Parroting". Does the text have unique human idiosyncrasies?
AGENT 4 (Adversarial Critic): Tries to prove the text is human and looks for "natural flaws" that AI rarely makes.

TEXT:
"{text[:2500]}"

OUTPUT FORMAT (Strict JSON):
{{
  "verdict": "AI-Generated" | "Human-Written",
  "confidence": 0.0-1.0,
  "agent_reports": {{
    "stylometrics": "AI-like consistency" | "Human-like variance",
    "logic": "Generic/Circular" | "Nuanced/Original",
    "personality": "Low/Robotic" | "High/Unique"
  }},
  "explanation": "Brief 2-sentence forensic summary"
}}
"""
        # Fallback logic for quota management
        model_names = ['gemini-2.5-flash', 'gemini-3.1-flash-lite-preview']
        response = None
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = await asyncio.to_thread(model.generate_content, prompt)
                if response:
                    logger.info(f"GEMINI ENGINE: Success using {model_name}")
                    break
            except Exception as e:
                # Silently log warning and continue to next model or finish
                logger.warning(f"Gemini {model_name} unavailable: {e}")
                continue
        
        if not response:
            return None

        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            import json
            return json.loads(json_match.group(0))
    except Exception as e:
        logger.error(f"Gemini audit failed: {e}")
    return None

# --- ENSEMBLE ORCHESTRATOR ---

async def detect_ai_text(text: str) -> Dict[str, Any]:
    """
    Main function using the Multi-Engine Ensemble approach.
    """
    if not text or len(text.strip()) < 50:
        return {
            "result": False,
            "confidence": 0.5,
            "error": "Text too short for reliable detection (min 50 chars)"
        }
    
    # 1. Run local statistical analysis
    stats = calculate_text_statistics(text)
    
    # 2. Query HF models in parallel (Modern DeBERTa-v3 is superior for GPT-4)
    hf_models = [
        "unikev/ai-detector-deberta-v3-large-v2",
        "openai-community/roberta-base-openai-detector"
    ]
    
    hf_tasks = [query_hf_model(m, text, settings.HUGGINGFACE_API_KEY) for m in hf_models]
    hf_results = await asyncio.gather(*hf_tasks)
    valid_hf_scores = [s for s in hf_results if s is not None]
    
    # 3. Get Gemini Audit
    gemini_audit = await get_gemini_audit(text)
    
    # --- CONTRADICTION-PENALIZED BAYESIAN AGGREGATION ---
    
    weights = {"hf": 0.45, "gemini": 0.35, "stats": 0.20}
    numerator = 0.0
    denominator = 0.0
    
    # Statistical baseline (Very reliable for structural fingerprints)
    s_score = stats["stat_score"]
    s_conf = 0.8 if stats["burstiness"] < 0.3 else 0.5 # High confidence in AI if burstiness is critically low
    
    numerator += s_score * s_conf * weights["stats"]
    denominator += s_conf * weights["stats"]

    # Neural evidence
    if valid_hf_scores:
        avg_hf = sum(valid_hf_scores) / len(valid_hf_scores)
        # PENALTY: If HF says 'Human' (low score) but Stats see 'Critically Low Burstiness', 
        # reduce HF reliability because it's likely a GPT-4 'blind spot'
        hf_reliability = 0.8
        if avg_hf < 0.2 and stats["burstiness"] < 0.3:
            logger.warning("Potential Neural Blind-Spot detected. Reducing HF reliability.")
            hf_reliability = 0.3 
            
        numerator += avg_hf * hf_reliability * weights["hf"]
        denominator += hf_reliability * weights["hf"]

    # Gemini evidence
    if gemini_audit:
        g_verdict = gemini_audit["verdict"]
        g_conf = gemini_audit["confidence"]
        g_score = g_conf if g_verdict == "AI-Generated" else (1.0 - g_conf)
        
        numerator += g_score * g_conf * weights["gemini"]
        denominator += g_conf * weights["gemini"]
    
    # Final Bayesian-lite Score
    final_ai_score = numerator / denominator if denominator > 0 else 0.5
    
    logger.info(f"FORENSIC ENSEMBLE: Score={final_ai_score:.2f}, Reliability={denominator:.2f}")
    
    is_ai = final_ai_score > 0.5
    confidence = final_ai_score if is_ai else (1.0 - final_ai_score)
    
    # Build detailed analysis response
    analysis_details = []
    if valid_hf_scores:
        analysis_details.append({
            "model": "Ensemble HF Classifiers",
            "verdict": "AI-Generated" if avg_hf > 0.5 else "Human-Written",
            "confidence": f"{int(max(avg_hf, 1-avg_hf)*100)}%",
            "analysis": "Analyzed deep neural patterns and statistical fingerprints."
        })
    
    if gemini_audit:
        reports = gemini_audit.get("agent_reports", {})
        analysis_details.append({
            "model": "Multi-Agent Forensic Audit",
            "verdict": gemini_audit["verdict"],
            "confidence": f"{int(gemini_audit['confidence']*100)}%",
            "analysis": f"{gemini_audit['explanation']} [Stylometrics: {reports.get('stylometrics')}, Personality: {reports.get('personality')}]"
        })
        
    analysis_details.append({
        "model": "Signature Statistics",
        "verdict": "AI-Generated" if stats["stat_score"] > 0.5 else "Human-Written",
        "confidence": f"{int(max(stats['stat_score'], 1-stats['stat_score'])*100)}%",
        "analysis": f"Burstiness: {stats['burstiness']:.2f}, Para Consistency: {stats['para_consistency']:.2f}, Entropy: {stats['entropy']:.2f}"
    })
    
    return {
        "result": is_ai,
        "confidence": float(confidence),
        "ai_score": float(final_ai_score),
        "real_score": float(1.0 - final_ai_score),
        "method": "Multi-Engine Ensemble",
        "analysis_details": analysis_details
    }
