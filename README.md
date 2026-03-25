# 🚦 TrafficMortality Analysis

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Framework-Flask-black)
![Scikit-Learn](https://img.shields.io/badge/Machine%20Learning-Scikit--Learrn-orange)
![Deployment](https://img.shields.io/badge/Deployment-Vercel%20Edge-black)

## 🌐 Live Deployment
**The intelligence dashboard is actively hosted on Vercel's Edge Network:**  
[**https://traffic-mortality-analysis.vercel.app/**](https://traffic-mortality-analysis.vercel.app/)

---

## 📖 Overview
The TrafficMortality Analysis system is a full-stack, AI-powered diagnostic application engineered to predict the severity of traffic accidents based on multi-dimensional spatial and meteorological data.

Moving beyond basic static analysis, this system is encapsulated in a Multi-Page Application (MPA) featuring real-time data visualizations, rigorous NaN-omission data pipelines, and a competitive machine learning architecture where three distinct algorithms are continuously evaluated on out-of-sample data.

---

## 🧠 Machine Learning Architecture
The predictive core processes 11 real-world variables (e.g., coordinates, barometric pressure, wind speed, junction proximity) and utilizes **TruncatedSVD** to mathematically compress the pipeline down to 8 orthogonal dimensions for real-time inference optimization.

**Evaluated Models:**
*   👑 **Multi-Layer Perceptron (MLP) Neural Network** *(Primary Inference Engine)*
*   🌳 **Decision Tree Classifier**
*   🧮 **Support Vector Machine (SVM)**

All models are trained strictly on an **80/20 train-test split**, and mathematically enforced by a **100% Strict NaN Omission** policy, preventing statistical hallucinations from `SimpleImputer` guessing techniques.

---

## 🛠 Project Structure
```text
Traffic Mortality Analysis/
├── app.py                     # The Core Flask Web Server & API Routing
├── train.py                   # The Offline Machine Learning Pipeline
├── requirements.txt           # Python dependency tree
├── vercel.json                # Vercel Serverless routing configuration
├── models/                    # Pre-computed AI State
│   ├── MLP_Neural_Net.pkl     # Primary Neural Engine Weights
│   ├── preprocessor.pkl       # Standardization scaler
│   └── svd.pkl                # Dimensionality Reduction engine
├── templates/                 # Global UI Views
│   ├── index.html             # Project Dashboard
│   ├── analytics.html         # Live Model Telemetry & Leaderboards
│   └── predictor.html         # Live Risk Inference UI
└── static/                    # Frontend Aesthetics (Glassmorphic)
    ├── app.js                 # Chart.js visualizations
    └── style.css              # Custom UI system
```

---

## 💻 Local Installation & Usage
To run the system locally on your administrative machine:

**1. Clone the repository:**
```bash
git clone https://github.com/Sid-369-2004/Traffic-Mortality-Analysis.git
cd "Traffic Mortality Analysis"
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Boot the Flask Server:**
```bash
python app.py
```
*The local development dashboard will natively launch on `http://127.0.0.1:5000`.*
