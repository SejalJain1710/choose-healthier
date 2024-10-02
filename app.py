import streamlit as st
import requests
from dotenv import load_dotenv
import os
import pandas as pd


def generate_health_analysis_gemini(product_name, user_preferences=None, order_history=None):
    prompt = f"""
    Provide a concise health analysis for the product(s) '{product_name}' based on the following pointers , and suggest healthier alternatives if available, keep this in bullet points
    - Nutritional Analysis (fats, sugar, sodium, and calories), give the values if possible
    - Harmful ingredients present
    - Does it comply with common diets (e.g., keto, vegan, low-carb)?
    - Diabetes/allergen friendly?
    - Misleading brand claims
    - Optimizations for better health outcomes

    DO NOT RECOMMEND PRODUCT NAME FROM THE SELECTED CART AS A HEALTHIER ALTERNATIVE. INSTEAD SEARCH FOR A HEALTHIER ALTERNATIVE BASED ON THE STORE AND MENU ITEM. THIS IS AN IMPORTANT POINT TO NOTE.For example : If the product is a vegan frozen pizza, suggest a cauliflower crust pizza with veggies as a healthier alternative.
    Previous orders to consider for better recommendations: {', '.join(order_history) if order_history else 'None'}.
    User preferences: {user_preferences if user_preferences else 'None'}.
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
        generated_text = result['candidates'][0]['content']['parts'][0]['text']
        return generated_text

    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"


def generate_evaluation_prompt(health_analysis):
    evaluation_prompt = f"""
    Evaluate the following health analysis based on the criteria of accuracy, precision, relevance, clarity, and usefulness. Provide scores out of 10 for each criterion, followed by an overall evaluation:

    Health Analysis: 
    {health_analysis}

    Criteria:
    - Accuracy (How factually correct is the analysis?)
    - Precision (How specific and detailed is the analysis?)
    - Relevance (How relevant is the analysis to the product?)
    - Clarity (How clear and understandable is the analysis?)
    - Usefulness (How actionable and useful is the analysis for making decisions?)

    Please provide an aggregated evaluation score out of 10 based on the above criteria.
    """
    return evaluation_prompt


def get_evaluation_from_llm(health_analysis):
    prompt = generate_evaluation_prompt(health_analysis)

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
        generated_evaluation = result['candidates'][0]['content']['parts'][0]['text']
        return generated_evaluation

    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"


def parse_health_analysis(text):
    sections = {
        "Nutritional Analysis": "",
        "Harmful Ingredients": "",
        "Diabetes/Allergen Friendly": "",
        "Misleading Brand Claims": "",
        "Optimizations for Better Health": ""
    }

    lines = text.split("\n")
    current_section = None

    for line in lines:
        if "Nutritional Analysis" in line:
            current_section = "Nutritional Analysis"
        elif "Harmful Ingredients" in line:
            current_section = "Harmful Ingredients"
        elif "Diabetes" in line or "Allergen" in line:
            current_section = "Diabetes/Allergen Friendly"
        elif "Misleading Brand Claims" in line:
            current_section = "Misleading Brand Claims"
        elif "Optimizations for Better Health" in line:
            current_section = "Optimizations for Better Health"
        elif current_section:
            sections[current_section] += line.strip() + " "

    df = pd.DataFrame(list(sections.items()), columns=["Category", "Details"])
    return df


healthier_alternatives = {
    "Whole Foods": {
        "Organic Granola Bar": ("Whole grain granola with no added sugar", 300),
        "Vegan Frozen Pizza": ("Cauliflower crust pizza with veggies", 600),
        "cauliflower crust pizza": ("Cauliflower crust pizza with veggies", 600),
        "Almond Milk": ("Unsweetened almond milk with added calcium", 150),
        "chai": ("Green tea with no added sugar", 50),
        "Baked Jalebi": ("Baked jalebi with minimal sugar", 150),
        "Kombucha": ("Low-sugar kombucha with natural flavors", 200)
    },
    "Indian Store": {
        "Samosa": ("Baked samosa with whole wheat crust", 100),
        "Pakora": ("Air-fried pakoras with chickpea flour", 120),
        "Jalebi": ("Baked jalebi with minimal sugar", 150),
        "Bhujia": ("Roasted bhujia with low oil", 80),
        "Basmati Rice": ("Brown basmati rice for added fiber", 200),
        "Dal": ("Lentil soup with less salt and oil", 150),
        "Whole Wheat Atta": ("Organic whole wheat atta for rotis", 100),
        "chai": ("Green tea with no added sugar", 50)
    }
}

grocery_products = {
    "Whole Foods": {
        "Snacks": ["Organic Granola Bar", "Vegan Frozen Pizza", "almond milk", "Baked Jalebi", "Organic Gran", "chai", "cauliflower crust pizza"],
        "Drinks": ["Almond Milk", "Kombucha", "chai"]
    },
    "Indian Store": {
        "Snacks": ["Samosa", "Pakora", "Jalebi", "Bhujia"],
        "Staples": ["Basmati Rice", "Dal", "Whole Wheat Atta"]
    }
}

previous_orders = ["Samosa", "Pakora", "Organic Granola Bar"]

if 'cart' not in st.session_state:
    st.session_state.cart = []

st.title("Product Health Analysis with Gemini AI")


grocery_stores = list(grocery_products.keys())
grocery_store = st.selectbox("Select a store:", grocery_stores)

if grocery_store:
    menu_categories = list(grocery_products[grocery_store].keys())
    selected_category = st.selectbox("Select a menu category:", menu_categories)

    product_names = grocery_products[grocery_store][selected_category]
else:
    product_names = []

selected_products = st.multiselect("Select product(s):", product_names)

if st.button("Add to Cart"):
    for product in selected_products:
        st.session_state.cart.append((grocery_store, product))
    st.success(f"Added to cart: {', '.join(selected_products)}")


if st.session_state.cart:
    st.subheader("Your Cart")
    cart_items = []
    for store, item in st.session_state.cart:
        price = healthier_alternatives.get(store, {}).get(item, ("N/A", "N/A"))[1]
        cart_items.append([store, item, price])

    cart_df = pd.DataFrame(cart_items, columns=["Store", "Product", "Price"])
    st.table(cart_df)


preferences = ["Gluten-Free", "Low-Carb", "Vegan", "Vegetarian", "Diabetes-Friendly", "Allergy-Free", "Paleo", "Keto"]
user_preferences = st.multiselect("Select your preferences:", preferences)

if st.button("Analyze Cart and Suggest Healthier Options"):
    if st.session_state.cart:
        with st.spinner("Generating health analysis and healthier alternatives..."):
            analysis_data = []
            for store, product in st.session_state.cart:
                analysis_text = generate_health_analysis_gemini(product, user_preferences, previous_orders)
                analysis_df = parse_health_analysis(analysis_text)
                st.subheader(f"Health Analysis for: {product}")
                st.table(analysis_df)

                # Get the evaluation from the LLM
                evaluation_text = get_evaluation_from_llm(analysis_text)
                st.subheader(f"Evaluation for: {product}")
                st.write(evaluation_text)

                healthier_option, healthier_price = healthier_alternatives.get(store, {}).get(product, ("No healthier option available", "N/A"))
                analysis_data.append([product, healthier_option, healthier_price])

            healthier_df = pd.DataFrame(analysis_data, columns=["Product", "Healthier Option", "Price"])
            st.subheader("Healthier Alternatives:")
            st.table(healthier_df)
    else:
        st.error("Your cart is empty. Please add products.")


feedback = st.text_area("Please share your feedback on the product analysis or the healthier options provided:")

if st.button("Submit Feedback"):
    if feedback:
        st.success("Thank you for your feedback!")
    else:
        st.error("Feedback cannot be empty.")