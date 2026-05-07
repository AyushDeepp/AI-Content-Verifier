import logging
import re
import math
import asyncio
import httpx
import json
from typing import Dict, Any, List, Optional
from core.config import settings
from huggingface_hub import InferenceClient
from groq import AsyncGroq
from core.key_rotator import get_gemini_rotator, get_groq_rotator

logger = logging.getLogger(__name__)

# --- ENGINE 1: STATISTICAL ANALYSIS (LOCAL) ---

def calculate_text_statistics(text: str) -> Dict[str, Any]:
    """
    Calculates advanced statistical cues: Burstiness, Entropy, Redundancy, and Stopword ratios.
    """
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    words = re.findall(r'\w+', text.lower())
    
    if not sentences or not words:
        return {"ai_score": 0.5, "reliability": 0.0, "details": "Insufficient text"}

    # 1. Burstiness (Sentence Length Variance)
    lengths = [len(s.split()) for s in sentences]
    avg_len = sum(lengths) / len(sentences)
    variance = sum((l - avg_len) ** 2 for l in lengths) / len(sentences)
    burstiness = math.sqrt(variance) / (avg_len + 1)
    
    # 2. Shannon Entropy (Vocabulary Complexity)
    word_freq = {}
    for w in words:
        word_freq[w] = word_freq.get(w, 0) + 1
    
    entropy = 0
    for count in word_freq.values():
        p = count / len(words)
        entropy -= p * math.log2(p)
    
    # 3. Redundancy (Lexical Diversity)
    unique_ratio = len(word_freq) / len(words)
    redundancy = 1.0 - unique_ratio # AI tends to be more redundant (lower unique ratio)
    
    # 4. Stopword Density
    # Common English stopwords (subset for performance)
    stopwords = {"the", "a", "an", "is", "are", "was", "were", "to", "of", "and", "in", "that", "it", "with", "as", "for", "on"}
    stopword_count = sum(1 for w in words if w in stopwords)
    stopword_density = stopword_count / len(words)
    
    # AI models often have a "sweet spot" of stopword density around 40-50%
    # Humans vary much more (very low or very high density)
    is_ai_stopword_density = 0.8 if 0.4 < stopword_density < 0.55 else 0.2

    # --- AGGREGATED STATISTICAL VOTE ---
    # High AI score if: Low Burstiness, Low Entropy, High Redundancy
    ai_score = 0.0
    if burstiness < 0.3: ai_score += 0.3 # Robotic consistency
    if entropy < 7.5: ai_score += 0.2    # Simple vocabulary
    if redundancy > 0.4: ai_score += 0.3 # Repetitive phrasing
    ai_score += is_ai_stopword_density * 0.2
    
    return {
        "ai_score": ai_score,
        "burstiness": burstiness,
        "entropy": entropy,
        "redundancy": redundancy,
        "stopword_density": stopword_density,
        "reliability": 0.8
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
        gemini_keys = get_gemini_rotator()
        if not gemini_keys.has_keys:
            return None
        
        model_names = ['gemini-flash-latest', 'gemini-2.0-flash-lite', 'gemini-2.0-flash']
        response = None
        
        for model_name in model_names:
            for attempt in range(gemini_keys.count):
                try:
                    genai.configure(api_key=gemini_keys.current)
                    model = genai.GenerativeModel(model_name)
                    response = await asyncio.to_thread(model.generate_content, prompt)
                    if response:
                        logger.info(f"GEMINI ENGINE: Success using {model_name}")
                        break
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        gemini_keys.rotate()
                        continue
                    logger.warning(f"Gemini {model_name} unavailable: {e}")
                    break
            if response:
                break
        
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

# --- ENGINE 4: GROQ LINGUISTIC ACCELERATOR ---

async def get_groq_audit(text: str) -> Dict[str, Any]:
    """Uses Groq (Llama 3) for ultra-fast linguistic analysis"""
    groq_keys = get_groq_rotator()
    if not groq_keys.has_keys:
        return None
        
    try:
        prompt = f"""Analyze the following text to detect AI-generation. Look for:
        1. Predictable transitions and circular logic.
        2. Lack of specific, messy human details.
        3. Stylometric rigidity.
        
        TEXT: "{text[:2000]}"
        
        RETURN JSON:
        {{
          "verdict": "AI-Generated" | "Human-Written",
          "confidence": 0.0-1.0,
          "explanation": "Brief 1-sentence reason"
        }}
        """
        
        for attempt in range(groq_keys.count):
            try:
                client = AsyncGroq(api_key=groq_keys.current)
                response = await client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                if "429" in str(e) or "rate" in str(e).lower():
                    groq_keys.rotate()
                    continue
                raise
    except Exception as e:
        logger.error(f"Groq audit failed: {e}")
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
        "Hello-SimpleAI/chatgpt-detector-roberta",
        "openai-community/roberta-base-openai-detector"
    ]
    
    hf_tasks = [query_hf_model(m, text, settings.HUGGINGFACE_API_KEY) for m in hf_models]
    hf_results = await asyncio.gather(*hf_tasks)
    valid_hf_scores = [s for s in hf_results if s is not None]
    
    
    # 3. Get LLM Audits
    gemini_task = get_gemini_audit(text)
    groq_task = get_groq_audit(text)
    
    gemini_audit, groq_audit = await asyncio.gather(gemini_task, groq_task)
    
    # --- CONTRADICTION-PENALIZED BAYESIAN AGGREGATION ---
    
    weights = {"hf": 0.40, "groq": 0.30, "gemini": 0.20, "stats": 0.10}
    numerator = 0.0
    denominator = 0.0
    
    # Statistical baseline (Very reliable for structural fingerprints)
    s_score = stats["ai_score"]
    s_conf = stats["reliability"]
    
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

    # Groq evidence
    if groq_audit:
        gr_verdict = groq_audit["verdict"]
        gr_conf = groq_audit["confidence"]
        gr_score = gr_conf if gr_verdict == "AI-Generated" else (1.0 - gr_conf)
        
        numerator += gr_score * gr_conf * weights["groq"]
        denominator += gr_conf * weights["groq"]
    
    # Final Bayesian-lite Score
    final_ai_score = numerator / denominator if denominator > 0 else 0.5
    
    logger.info(f"FORENSIC ENSEMBLE: Score={final_ai_score:.2f}, Reliability={denominator:.2f}")
    
    is_ai = final_ai_score > 0.5
    confidence = final_ai_score if is_ai else (1.0 - final_ai_score)
    
    # Build detailed analysis response
    analysis_details = []
    if valid_hf_scores:
        analysis_details.append({
            "model": "Neural Classifier",
            "verdict": "AI-Generated" if avg_hf > 0.5 else "Human-Written",
            "confidence": f"{int(max(avg_hf, 1-avg_hf)*100)}%",
            "analysis": (
                f"The text was analyzed using neural networks trained on millions of human and AI-generated "
                f"text samples. These models detect deep statistical patterns in word choices and sentence "
                f"structures that are invisible to the human eye but reliably distinguish machine-generated text."
            )
        })
    
    if gemini_audit:
        reports = gemini_audit.get("agent_reports", {})
        analysis_details.append({
            "model": "Forensic Audit",
            "verdict": gemini_audit["verdict"],
            "confidence": f"{int(gemini_audit['confidence']*100)}%",
            "analysis": (
                f"{gemini_audit['explanation']} "
                f"Writing style: {reports.get('stylometrics', 'N/A')}. "
                f"Personality markers: {reports.get('personality', 'N/A')}. "
                f"This analysis examines whether the text shows genuine human idiosyncrasies "
                f"(personal anecdotes, unique word choices, natural flaws) or robotic consistency."
            )
        })

    if groq_audit:
        analysis_details.append({
            "model": "Linguistic Analysis",
            "verdict": groq_audit["verdict"],
            "confidence": f"{int(groq_audit['confidence']*100)}%",
            "analysis": (
                f"{groq_audit['explanation']} "
                f"This check looks for predictable transitions, circular reasoning, "
                f"and lack of specific, messy human details that AI text typically lacks."
            )
        })
        
    analysis_details.append({
        "model": "Statistical Analysis",
        "verdict": "AI-Generated" if stats['ai_score'] > 0.5 else "Human-Written",
        "confidence": f"{int(stats['ai_score']*100)}%",
        "analysis": (
            f"Burstiness: {stats['burstiness']:.2f} — measures how much sentence length varies "
            f"(AI text tends to have very uniform sentence lengths, humans vary more). "
            f"Entropy: {stats['entropy']:.2f} — measures vocabulary richness "
            f"(AI uses simpler, more predictable word choices). "
            f"Redundancy: {stats['redundancy']:.2f} — measures how often words/phrases are repeated "
            f"(AI tends to be more repetitive)."
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
