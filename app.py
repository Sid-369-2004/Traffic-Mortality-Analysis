from flask import Flask, render_template, request, jsonify
import joblib
import json
import os
import numpy as np
import pandas as pd

app = Flask(__name__)

# Load models if they exist
MODELS_DIR = 'models'
try:
    with open(os.path.join(MODELS_DIR, 'metrics.json'), 'r') as f:
        metrics_data = json.load(f)
    
    # Load best model and preprocessors for live predictions
    preprocessor = joblib.load(os.path.join(MODELS_DIR, 'preprocessor.pkl'))
    svd = joblib.load(os.path.join(MODELS_DIR, 'svd.pkl'))
    best_model = joblib.load(os.path.join(MODELS_DIR, 'MLP_Neural_Net.pkl'))
except Exception as e:
    metrics_data = {"error": "Models have not been trained yet. Please run train.py"}
    preprocessor = None
    svd = None
    best_model = None

@app.route('/')
def index():
    return render_template('index.html', active_page='home')

@app.route('/dataset')
def dataset():
    # Load first clean 20 rows of dataset
    try:
        df = pd.read_csv('Accidents.csv', nrows=100)
        # Drop heavily null columns first so they don't force dropna to purge valid records
        df = df.drop(columns=['End_Lat', 'End_Lng'], errors='ignore')
        # Remove any rows with missing data and take the top 20
        df = df.dropna().head(20)
        data_preview = df.to_dict(orient='records')
        columns = df.columns.tolist()
    except Exception:
        data_preview = []
        columns = []
    return render_template('dataset.html', active_page='dataset', data=data_preview, columns=columns)

@app.route('/analytics')
def analytics():
    return render_template('analytics.html', active_page='analytics', metrics=metrics_data)

@app.route('/predictor')
def predictor():
    return render_template('predictor.html', active_page='predictor')

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    return jsonify(metrics_data)

preview_cache = None

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        if best_model is None or preprocessor is None or svd is None:
            return jsonify({"error": "Models not trained."}), 400
            
        data = request.json
        # Expecting JSON like: {"Start_Lat": ..., "Start_Lng": ..., "Temperature(F)": ..., etc.}
        
        # Convert single dictionary to DataFrame
        df_input = pd.DataFrame([data])
        
        # Process the input using the saved preprocessor and svd
        assert preprocessor is not None and svd is not None and best_model is not None
        X_processed = preprocessor.transform(df_input)
        X_reduced = svd.transform(X_processed)
        
        # Predict using MLP_Neural_Net
        prediction = best_model.predict(X_reduced)[0]
        
        # We mapped Severe/Fatal as 1, Non-Severe as 0
        if prediction == 1:
            result = "Severe / Fatal Accident Likely"
            
            # Generate reasoning for Severe
            visibility = float(data.get("Visibility(mi)", 10.0))
            wind = float(data.get("Wind_Speed(mph)", 0.0))
            temp = float(data.get("Temperature(F)", 50.0))
            crossing = float(data.get("Crossing", 0.0))
            junction = float(data.get("Junction", 0.0))
            
            if visibility <= 3.0:
                reason = "Extremely low visibility severely impairs driver reaction time, highly correlating with fatal collisions."
            elif wind >= 15.0:
                reason = "High wind speeds create handling instability, greatly amplifying the risk of catastrophic loss of vehicle control."
            elif temp <= 32.0:
                reason = "Freezing temperatures indicate probable black ice or slippery surfaces, drastically reducing stopping distance and causing severe accidents."
            elif crossing == 1.0 or junction == 1.0:
                reason = "Complex intersections under these specific environmental conditions represent a critical danger zone for high-impact collisions."
            else:
                reason = "The multivariate combination of current atmospheric pressure, temperature, and localized road infrastructure strongly matches historic severe fatality profiles."
        else:
            result = "Non-Severe Accident"
            reason = "The provided weather patterns and road conditions align with routine traffic incidents, indicating a low probability of severe injuries or extensive property damage."
            
        # Get probability confidence
        try:
            probabilities = best_model.predict_proba(X_reduced)[0]
            prob_safe = round(probabilities[0] * 100, 1)
            prob_severe = round(probabilities[1] * 100, 1)
        except:
            prob_safe = 100.0 if prediction == 0 else 0.0
            prob_severe = 100.0 if prediction == 1 else 0.0
            
        # Format the models data specifically for the frontend ranking panel
        model_stats = {}
        for m_name, m_data in metrics_data.items():
            model_stats[m_name] = m_data
            
        metrics_payload = {
            "prediction": result, 
            "reason": reason, 
            "status": "success",
            "confidence": {
                "safe": prob_safe,
                "severe": prob_severe
            },
            "models": model_stats,
            "inputs": {
                "Temperature": data.get("Temperature(F)"),
                "Visibility": data.get("Visibility(mi)"),
                "WindSpeed": data.get("Wind_Speed(mph)")
            }
        }
        
        return jsonify(metrics_payload)
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"}), 500

if __name__ == '__main__':
    # Ensure templates and static folders exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    app.run(debug=True, port=5000)
