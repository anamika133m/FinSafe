#FinSafe - Misleading Financial Content Detection
import streamlit as st
import speech_recognition as sr
from textblob import TextBlob
import os

HIGH_RISK_KEYWORDS = [
    "guaranteed returns", "double your money", "risk free", "risk-free",
    "crorepati", "100% profit", "assured returns", "no loss", "100% returns", "paisa double"
]

MEDIUM_RISK_KEYWORDS = [
    "multibagger", "hidden gem", "tips", "recommended",
    "hot stock", "breakout", "wealth creation"
]

# Text Analysis Function
def analyze_text(text):
    """Analyse text for risk level using sentiment + keywords"""
    
    if not text or text.strip() == "":
        return None
    
    text_lower = text.lower()
    
    # Sentiment analysis
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity
    
    if sentiment_score > 0:
        sentiment_label = "Positive"
    elif sentiment_score < 0:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"
    
    # Keyword-based risk detection
    risk_level = "Low"
    matched_keywords = []
    
    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in text_lower:
            risk_level = "High"
            matched_keywords.append(keyword)
    
    if risk_level != "High":
        for keyword in MEDIUM_RISK_KEYWORDS:
            if keyword in text_lower:
                risk_level = "Medium"
                matched_keywords.append(keyword)
    
    # SEBI logic: Very negative sentiment + Low risk keywords = raise to Medium
    if sentiment_score < -0.5 and risk_level == "Low":
        risk_level = "Medium"
        matched_keywords.append("negative sentiment with no keywords")
    
    # Generate explanation
    if risk_level == "High":
        explanation = f"⚠️ High risk: Contains misleading claims like {', '.join(matched_keywords[:2])}. Violates SEBI guidelines."
    elif risk_level == "Medium":
        explanation = f"📊 Medium risk: {', '.join(matched_keywords[:2]) if matched_keywords else 'Negative sentiment'} — review carefully."
    else:
        explanation = "✅ Low risk: No misleading claims detected. Content appears compliant."
    
    return {
        "risk_level": risk_level,
        "sentiment": sentiment_label,
        "sentiment_score": round(sentiment_score, 2),
        "matched_keywords": matched_keywords,
        "explanation": explanation
    }

# Audio to Text
def audio_to_text(audio_file_path):
    """Convert .wav audio file to text"""
    
    recognizer = sr.Recognizer()
    
    with sr.AudioFile(audio_file_path) as source:
        audio_data = recognizer.record(source)
    
    text = recognizer.recognize_google(audio_data)
    return text

# Streanlit UI
st.set_page_config(page_title="FinSafe", page_icon="🔒")
st.title("🔒 FinSafe - Misleading Financial Content Detection")
st.markdown("*Based on SEBI guidelines | Audio support: .wav files only*")

# Input type selection
input_type = st.radio("Choose input type:", ["📝 Text", "🎵 Audio File (.wav)"])

# Text input
if input_type == "📝 Text":
    user_text = st.text_area("Enter financial text/claim:", height=150)
    
    if st.button("Analyze Risk"):
        if user_text and user_text.strip():
            result = analyze_text(user_text)
            
            if result:
                # Display results
                if result["risk_level"] == "High":
                    st.error(f"**Risk Level:** {result['risk_level']}")
                elif result["risk_level"] == "Medium":
                    st.warning(f"**Risk Level:** {result['risk_level']}")
                else:
                    st.success(f"**Risk Level:** {result['risk_level']}")
                
                st.write(f"**Sentiment:** {result['sentiment']} (Score: {result['sentiment_score']})")
                st.write(f"**Explanation:** {result['explanation']}")
                
                if result["matched_keywords"]:
                    st.write(f"**Matched keywords:** {', '.join(result['matched_keywords'])}")
            else:
                st.info("Please enter some text to analyze.")
        else:
            st.info("Please enter some text to analyze.")

# Audio file input
else:
    st.markdown("### Upload a pre-recorded .wav file")
    st.caption("Example: Record on your phone as 'test.wav' and upload here")
    
    audio_file = st.file_uploader("Choose a .wav file", type=["wav"])
    
    if audio_file is not None:
        # Save temporarily
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_file.getbuffer())
        
        st.success(f"✅ File loaded: {audio_file.name}")
        
        if st.button("Convert & Analyze Risk"):
            st.write("🔄 Converting audio to text...")
            text = audio_to_text("temp_audio.wav")
            st.write(f"📝 **Transcribed text:** \"{text}\"")
            
            result = analyze_text(text)
            
            if result:
                if result["risk_level"] == "High":
                    st.error(f"**Risk Level:** {result['risk_level']}")
                elif result["risk_level"] == "Medium":
                    st.warning(f"**Risk Level:** {result['risk_level']}")
                else:
                    st.success(f"**Risk Level:** {result['risk_level']}")
                
                st.write(f"**Sentiment:** {result['sentiment']} (Score: {result['sentiment_score']})")
                st.write(f"**Explanation:** {result['explanation']}")
                
                if result["matched_keywords"]:
                    st.write(f"**Matched keywords:** {', '.join(result['matched_keywords'])}")
            else:
                st.info("Could not analyze. Please check the audio content.")
        
        # Clean up temp file
        if os.path.exists("temp_audio.wav"):
            os.remove("temp_audio.wav")
