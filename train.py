import pandas as pd
import numpy as np
import os
import json
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.decomposition import TruncatedSVD
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib

def main():
    print("Loading a sample of 25,000 rows from Accidents.csv to allow fast local training...")
    try:
        # Read a smaller chunk for local machine feasibility (SVM takes O(N^3) time)
        df = pd.read_csv('Accidents.csv', nrows=15000)
    except FileNotFoundError:
        print("Error: Accidents.csv not found. Please ensure it is in the current directory.")
        return

    # 1. Target Mapping: Binary Classification for Mortality / Severity
    # We will classify Severity 3 & 4 as Severe/Fatal (1) and 1 & 2 as Non-Severe (0)
    print("Preprocessing data and mapping target variable...")
    df['Target'] = df['Severity'].apply(lambda x: 1 if x >= 3 else 0)

    # 2. Feature Selection
    num_features = ['Start_Lat', 'Start_Lng', 'Temperature(F)', 'Humidity(%)', 
                    'Pressure(in)', 'Visibility(mi)', 'Wind_Speed(mph)']
    cat_features = ['Sunrise_Sunset']
    bool_features = ['Crossing', 'Junction', 'Traffic_Signal']

    for b in bool_features:
        if b in df.columns:
            df[b] = df[b].astype(float)

    selected_features = num_features + cat_features + bool_features
    
    # Strict Data Cleaning: Remove any rows containing NULL/NaN values instead of imputing
    df = df.dropna(subset=selected_features + ['Target'])
    
    X = df[selected_features]
    y = df['Target']

    # 3. Preprocessing Pipelines (Imputers removed per strict data cleaning rules)
    num_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])

    cat_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_transformer, num_features + bool_features),
            ('cat', cat_transformer, cat_features)
        ])

    X_processed = preprocessor.fit_transform(X)

    # 4. Dimensionality Reduction (PCA via SVD)
    print("Applying PCA / TruncatedSVD for Dimensionality Reduction...")
    # Reduce components while keeping most variance to help models run faster
    n_comps = min(X_processed.shape[1] - 1, 8)
    svd = TruncatedSVD(n_components=n_comps, random_state=42)
    X_reduced = svd.fit_transform(X_processed)

    X_train, X_test, y_train, y_test = train_test_split(X_reduced, y, test_size=0.2, random_state=42, stratify=y)
    
    # 5. Model Initialization - Tuned to maximize MLP Neural Network performance
    models = {
        "Decision_Tree": DecisionTreeClassifier(random_state=42, max_depth=5),
        "SVM": SVC(kernel='rbf', C=0.5, random_state=42),
        "MLP_Neural_Net": MLPClassifier(hidden_layer_sizes=(128, 64, 32), activation='relu', solver='adam', alpha=0.0001, max_iter=800, random_state=42)
    }

    metrics_results = {}

    # Define the models directory
    os.makedirs('models', exist_ok=True)
    joblib.dump(preprocessor, 'models/preprocessor.pkl')
    joblib.dump(svd, 'models/svd.pkl')

    # 6. Training & Evaluation loop
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        metrics_results[name] = {
            "Accuracy": round(acc * 100, 2),
            "Precision": round(prec * 100, 2),
            "Recall": round(rec * 100, 2),
            "F1_Score": round(f1 * 100, 2)
        }
        
        # Save model
        joblib.dump(model, f'models/{name}.pkl')
        print(f"{name} completed: Accuracy {acc:.2f}")

    # 7. Save metrics JSON
    with open('models/metrics.json', 'w') as f:
        json.dump(metrics_results, f, indent=4)
        
    print("Training complete! Models and metrics have been saved.")

if __name__ == '__main__':
    main()
