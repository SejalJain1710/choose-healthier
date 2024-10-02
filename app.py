import streamlit as st
import requests
from dotenv import load_dotenv
import os

# Function to generate health analysis
def generate_health_analysis_gemini(product_name, user_preferences=None):
    prompt = f"""
    Provide a detailed health analysis of the product '{product_name}' based on the following pointers:
    - Nutritional Analysis (e.g., presence of fats, sugar, sodium, and calories)
    - Degree of processing and nutrient deficit
    - Harmful ingredients present
    - Does it comply with common diets (e.g., keto, vegan, low-carb)?
    - Is it diabetes/allergen friendly?
    - Are there misleading brand claims?
    - What optimizations can be suggested for better health outcomes?
    
    For user-specific analysis, consider the following preferences: {user_preferences if user_preferences else 'None'}.
    """

    gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            f"{gemini_api_url}?key={api_key}",
            json=payload,
            headers=headers
        )
        response.raise_for_status()

        result = response.json()
        st.write(result) 

        generated_text = result.get('contents', [{'parts': [{'text': 'No content found'}]}])[0]['parts'][0]['text']
        return generated_text

    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

st.title("Product Health Analysis with Gemini AI")

product_name = st.text_input("Enter the product name:")
user_preferences = st.text_area("Optional: Enter user-specific preferences (e.g., dietary restrictions, health conditions):")

if st.button("Analyze Product"):
    if product_name:
        with st.spinner("Generating health analysis..."):
            analysis = generate_health_analysis_gemini(product_name, user_preferences)
            st.subheader("Health Analysis:")
            st.write(analysis)
    else:
        st.error("Please enter a product name.")