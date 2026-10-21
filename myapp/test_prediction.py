import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geonexus.settings')
django.setup()

import pandas as pd
import joblib
from myapp.services import extract_dem_terrain, get_live_rainfall

MODEL_PATH = os.path.join(os.path.dirname(__file__), "geonexus_xgb_model.joblib")
xgb_data = joblib.load(MODEL_PATH)
model = xgb_data['model']

# ടെസ്റ്റ് കോർഡിനേറ്റ് (മൂന്നാർ മലയോര മേഖല)
lat, lon = 10.0749, 76.7991

alt, slope = extract_dem_terrain(lat, lon)
rain = get_live_rainfall(lat, lon)

input_df = pd.DataFrame([{
    'latitude': lat,
    'longitude': lon,
    'altitude': alt,
    'slope': slope,
    'rainfall': rain
}])

prob = float(model.predict_proba(input_df)[0][1])

print("\n--- GEONEXUS LIVE TEST RESULT ---")
print(f"Location    : ({lat}, {lon})")
print(f"Altitude    : {alt} m")
print(f"Slope       : {slope} degrees")
print(f"Rainfall    : {rain} mm")
print(f"Risk Score  : {round(prob * 100, 2)}%")

if prob >= 0.70:
    print("Status      : High Risk (റെഡ് അലേർട്ട്)")
elif prob >= 0.35:
    print("Status      : Moderate Risk (ഓറഞ്ച് അലേർട്ട്)")
else:
    print("Status      : Low Risk (സുരക്ഷിതം)")