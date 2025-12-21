"""
Quick test script to verify AI detection is working
Run this after the backend is running
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"

# Sample texts for testing
AI_TEXT = """
It is important to note that artificial intelligence has revolutionized numerous industries. 
Furthermore, machine learning algorithms have demonstrated remarkable capabilities in pattern recognition. 
Moreover, deep learning models continue to advance at an unprecedented rate. 
Additionally, natural language processing has enabled sophisticated text analysis.
"""

HUMAN_TEXT = """
I think AI is pretty cool, but honestly I'm not sure how it all works. 
My friend was telling me about ChatGPT the other day and I was like, wow that's crazy! 
I tried it myself and it's actually really helpful for brainstorming ideas.
What do you guys think about all this AI stuff?
"""

def test_text_detection(text, description):
    """Test text detection endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"{'='*60}")
    print(f"Text preview: {text[:100]}...")
    
    # Note: This test requires authentication
    # You'll need to login first and get a token
    print("\n⚠️  This requires authentication. Please:")
    print("1. Login to the app")
    print("2. Get your JWT token from browser DevTools")
    print("3. Use it in the Authorization header")
    print("\nOr test directly from the frontend UI!")

if __name__ == "__main__":
    print("AI Content Verifier - Detection Test")
    print("=" * 60)
    
    # Test AI-generated text
    test_text_detection(AI_TEXT, "AI-Generated Text (Formal)")
    
    # Test human text
    test_text_detection(HUMAN_TEXT, "Human-Written Text (Casual)")
    
    print("\n" + "="*60)
    print("✅ To test properly, use the frontend UI at http://localhost:3000")
    print("   Navigate to the Text Verifier page and paste the sample texts above")
    print("="*60)
