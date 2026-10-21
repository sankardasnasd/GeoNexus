import os
import joblib
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

CSV_PATH = r"C:\Users\GAYATHRI\Downloads\lanslide\kerala_landslides_with_dem_slope_fixed.csv"

if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"Cleaned CSV dataset missing at: {CSV_PATH}")

print("Loading cleaned dataset...")
df = pd.read_csv(CSV_PATH)

pos_df = pd.DataFrame()
pos_df['latitude'] = df['latitude'].astype(float)
pos_df['longitude'] = df['longitude'].astype(float)
pos_df['altitude'] = df['altitude'].astype(float)
pos_df['slope'] = df['slope'].astype(float)

# കേരളത്തിലെ മൺസൂൺ മഴയുടെ സാമ്പിൾ വെയ്റ്റേജ് (mm)
np.random.seed(42)
pos_df['rainfall'] = np.random.uniform(60.0, 240.0, size=len(df))
pos_df['target'] = 1

n_samples = len(pos_df)
neg_df = pd.DataFrame()
neg_df['latitude'] = np.random.uniform(8.3, 12.8, size=n_samples)
neg_df['longitude'] = np.random.uniform(75.2, 76.5, size=n_samples)
neg_df['altitude'] = np.random.uniform(5.0, 80.0, size=n_samples)  # താഴ്ന്ന പ്രദേശങ്ങൾ
neg_df['slope'] = np.random.uniform(0.0, 10.0, size=n_samples)     # പരന്ന സമതലം
neg_df['rainfall'] = np.random.uniform(0.0, 30.0, size=n_samples)  # കുറഞ്ഞ മഴ
neg_df['target'] = 0

full_df = pd.concat([pos_df, neg_df], ignore_index=True).sample(frac=1, random_state=42)

features = ['latitude', 'longitude', 'altitude', 'slope', 'rainfall']
X = full_df[features]
y = full_df['target']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("Training XGBoost Classifier...")
model = XGBClassifier(
    n_estimators=120,
    max_depth=5,
    learning_rate=0.08,
    eval_metric='logloss',
    random_state=42
)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {round(acc * 100, 2)}%")
print(classification_report(y_test, y_pred))

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_SAVE_PATH = os.path.join(CURRENT_DIR, "geonexus_xgb_model.joblib")

joblib.dump({
    'model': model,
    'features': features
}, MODEL_SAVE_PATH)

print(f"\n[SUCCESS] New reliable model saved at:\n{MODEL_SAVE_PATH}")