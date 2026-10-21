# GeoNexus
GeoNexus is an AI disaster management platform using XGBoost, SHAP, 30m SRTM DEM, and live weather to predict landslides, alongside sensor Shake-to-SOS alerts and relief camp coordination.

# 🌍 GeoNexus: AI-Driven Landslide Hazard Warning & Disaster Response System

**GeoNexus** is an intelligent disaster prediction, early warning, and relief coordination ecosystem designed to mitigate landslide risks and streamline emergency rescue operations. The system integrates machine learning with spatial elevation datasets and real-time meteorological feeds, backed by web portals for administrative authorities and mobile apps for field responders and citizens.

---

## 🛠️ System Architecture & Technology Stack

The platform is structured into two core technology tiers:

### 1. Web Portals (Python & Django)
Centralized administration and camp logistics command centers.
* **Backend:** Python, Django, Django  Framework
* **Machine Learning & Geospatial:** XGBoost, SHAP (Explainable AI), Rasterio (Horn's 3x3 Slope Algorithm), Pandas, NumPy
* **External APIs:** 30m SRTM Digital Elevation Model (DEM), OpenWeatherMap API
* **Database:** SQLite / PostgreSQL / MySQL

### 2. Mobile Applications (Flutter & Dart)
Field-ready, low-latency mobile interfaces for volunteers, response teams, and citizens.
* **Framework:** Flutter & Dart
* **Key Integrations:** Accelerometer Sensor Shake Detection, Reverse Geocoding (`geocoding`), GPS Location Tracking (`location`), Native Telephony (`url_launcher`)

---

## 👥 Roles & Module Breakdown

### 🌐 Web Portals (Django)

#### 1. Admin Command Portal
* **System Monitoring:** Complete oversight of regional disaster metrics, high-hazard zones, and user activity.
* **Coordination & Approvals:** Review and approve registered Camp Coordinators and Emergency Response Teams (ERT).
* **Resource Allocation:** Monitor district-wide relief supplies, fund contributions, and unresolved SOS transmissions.

#### 2. Camp Coordinator Portal
* **Camp Infrastructure:** Manage relief camp capacity, occupancy records, and shelter details.
* **Requirement Tracking:** Post live supply requests (food, medicines, clothing, sanitation) directly to the network.
* **Contribution Ledger:** Track and verify public monetary donations and incoming supply allocations.

---

### 📱 Mobile Applications (Flutter)

#### 3. Citizen / User App
* **Live Hazard Assessment:** Search any location or auto-detect current GPS coordinates to evaluate landslide risk probability via XGBoost.
* **Explainable AI (SHAP):** Transparently view environmental risk drivers (slope angle, precipitation, altitude) via color-coded impact charts.
* **Emergency SOS & Shake Detection:** Hardware-accelerated accelerometer trigger (with toggle protection) to transmit emergency alerts and GPS coordinates to authorities without needing to tap the screen.
* **Relief & Donations:** View verified camp requirements and contribute financial relief funds.

#### 4. Emergency Response Team (ERT) App
* **SOS Incident Dispatch:** Receive immediate alerts with geolocation tags and reverse-geocoded place names from individuals in distress.
* **Rescue Routing:** Direct access to victim coordinates and one-tap emergency calling to initiate rapid on-ground response.

#### 5. Volunteer App
* **Camp Supply Fulfillment:** Browse verified requirements posted by camp coordinators and volunteer for ground distribution.
* **Field Updates:** Report real-time site observations, abnormal soil cracks, or flash runoff indicators to authorities.

---

## 🧠 Core Intelligence Features

* **Real-Time Data Fusion:** Blends spatial terrain steepness from 30m SRTM DEM GeoTIFFs with live precipitation volume from OpenWeather.
* **Tree-Based Inference:** Predicts categorical hazard levels (Low, Moderate, High) using an optimized XGBoost classification model.
* **Explainability with SHAP:** Breaks down predictions into feature-level percentage influences (e.g., *Geographical Slope +54%*, *Live Rainfall +32%*), avoiding black-box decision making.
* **Accidental Shake Guard:** Debounced sensor logic ensuring phone agitation only sends SOS when deliberately armed by the user.

---

## 🚀 Getting Started

### Backend Setup (Django)

git clone [https://github.com/your-username/geonexus.git](https://github.com/your-username/geonexus.git)
cd geonexus/backend
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
