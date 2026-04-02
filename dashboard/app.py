import streamlit as st
import joblib
import re

# Load trained model and vectorizer
model_data = joblib.load("ml_models/saved_models/baseline_model.pkl")
model = model_data['model']
vectorizer = model_data['vectorizer']

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-z\s]", "", text)
    return text

st.set_page_config(page_title="Fake News Detector", layout="centered")

st.title("📰 Real-Time Fake News Detection System")
st.write("Enter any news article text below to check if it is Fake or Real.")

news_input = st.text_area("Paste News Text Here:", height=200)

if st.button("Analyze News"):
    if news_input.strip() == "":
        st.warning("Please enter some news text.")
    else:
        cleaned = clean_text(news_input)
        vectorized = vectorizer.transform([cleaned])
        prediction = model.predict(vectorized)[0]
        probas = model.predict_proba(vectorized)[0]
        confidence = probas.max()

        st.subheader("Result:")
        
        # Debug info
        with st.expander("Debug Info"):
            st.write(f"Original text: {news_input}")
            st.write(f"Cleaned text: {cleaned}")
            st.write(f"Raw prediction: {prediction}")
            st.write(f"Probabilities: Real={probas[0]:.4f}, Fake={probas[1]:.4f}")

        if prediction == 1:
            st.error(f"⚠ This news is likely FAKE")
        else:
            st.success(f"✔ This news appears REAL")

        st.write(f"Confidence Score: {confidence:.2%}")
