# choose-healthier

# Snacks and Dishes Information Web App

This project consists of a **Flask API** that provides information about snacks and dishes from a CSV dataset, and a **Streamlit** web application to interact with the API and visualize the data.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technologies](#technologies)
- [Setup Instructions](#setup-instructions)
- [Running the Project](#running-the-project)
  - [Streamlit App](#streamlit-app)
- [Dataset](#dataset)
- [Endpoints](#endpoints)

## Overview

The project allows users to filter snacks and dishes based on different categories, such as the type of course (starter, dessert, etc.), ingredients, and other attributes. The backend is built using **Flask**, and the frontend uses **Streamlit** for user interaction.

## Features

- Filter products based on different attributes like course.
- View a list of Indian snacks and dishes, enriched with proprietary claims and other details.
- Simple and fast API integration for returning filtered results.

## Technologies

- **Flask**: Backend API
- **Streamlit**: Frontend Web App
- **Pandas**: For reading and processing CSV datasets
- **Flask-CORS**: To handle Cross-Origin Resource Sharing (CORS)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/snacks-and-dishes-app.git
cd snacks-and-dishes-app

### 2. Create a Virtual Environment and Activate It
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

### 2. Create a Virtual Environment and Activate It
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

### 3. Install Required Dependencies
```bash
pip install -r requirements.txt

### 4. Add Your CSV Datasets
Place your data in the root directory of the project.

## Running the project
Streamlit App
Open another terminal and navigate to the project directory.
Run the Streamlit app:
```bash
streamlit run streamlit_app.py
The Streamlit web app will open in your default web browser.

## Dataset

## Endpoints
### GET /products
Fetch products based on the `course` query parameter (optional).

- **URL**: `http://localhost:5000/products`
- **Query Parameter**: `course` (optional)

#### Example Request:

```bash
curl "http://localhost:5000/products?course=dessert"
Response: A JSON array of products filtered by the course.
