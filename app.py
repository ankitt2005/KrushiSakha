from flask import Flask, request, jsonify, render_template,redirect, url_for,flash, send_from_directory
import os
os.environ['TF_USE_LEGACY_KERAS'] = '1'
import pickle
import numpy as np
import os
import requests
from datetime import datetime, timedelta
from werkzeug.exceptions import BadRequest
import forms

from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from datetime import datetime, timedelta
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import schedule
import time
import threading
import json
import os
from twilio.rest import Client
from celery import Celery
import logging
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename
import numpy as np
import keras
from keras.models import load_model
from PIL import Image
from typing import Dict, List, Any
import os
from werkzeug.utils import secure_filename
import numpy as np
from keras.preprocessing import image
import numpy as np
import json
import uuid
import os
import tensorflow as tf
import groq
from dotenv import load_dotenv

load_dotenv()
try:
    groq_client = groq.Client(api_key=os.environ.get("GROQ_API_KEY"))
except Exception as e:
    groq_client = None

def get_disease_info(disease_name):
    base_info = {"name": disease_name, "cause": "Analysis pending...", "cure": "Consult an expert."}
    if "healthy" in disease_name.lower():
        base_info["cause"] = "Your plant is completely healthy! No pathogens detected."
        base_info["cure"] = "Keep up the good work! Ensure proper watering, sunlight, and timely fertilization."
        return base_info
        
    if not groq_client: return base_info
    
    prompt = f"You are an expert plant pathologist. The AI detected '{disease_name}'. Provide exactly a JSON response with two keys: 'cause' (an array of 2-3 short bullet points explaining the pathogens or conditions) and 'cure' (an array of 2-3 short bullet points explaining chemical and organic treatments). Make them highly practical for a farmer. Return ONLY valid JSON."
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        base_info.update(data)
    except Exception as e:
        print(f"Groq API Error: {e}")
    return base_info

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")

try:
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    else:
        twilio_client = None
except Exception as e:
    twilio_client = None

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' 
db = SQLAlchemy(app)
app.config['SECRET_KEY']='mykey'  # Replace with a secure key in production
migrate = Migrate(app, db)

# Disease Model Configuration




# Weather API Configuration - Updated to WeatherAPI.com
WEATHER_API_KEY = '94f53f8fc64d498ba1f92442250709'
WEATHER_BASE_URL = 'https://api.weatherapi.com/v1'
USDA_API_KEY = 'rEnj0yO0MhdlNRbc0ILPYqTb7LdaTapC5mEtrmJJ'
USDA_BASE_URL = 'https://quickstats.nass.usda.gov/api'
# Global variables to store loaded models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    message = db.Column(db.Text, nullable=False)
# models.py - Keep your separate tables
class LoginStore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(15), unique=True, nullable=True)
    Email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(100), nullable=False)
    coins   = db.Column(db.Integer, default=0, nullable=False)
    last_login   = db.Column(db.DateTime, nullable=True)

class RegisterStore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(120), unique=True)
    Phone_number= db.Column(db.String(15), unique=True, nullable=True)
    password = db.Column(db.String(100), nullable=False)
    confirm_password = db.Column(db.String(100), nullable=False)

class Farmerstore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    farm_size = db.Column(db.Float, nullable=False)
    crop_types = db.Column(db.String(200), nullable=False)
    irrigation_methods = db.Column(db.String(200), nullable=False)
    soil_type = db.Column(db.String(100), nullable=False)
    experience_level = db.Column(db.String(50), nullable=False)

class OrderStore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)


class RentStore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    rentdate = db.Column(db.String(50), nullable=False)
    return_date = db.Column(db.String(50), nullable=False)

class CourseCompletion(db.Model):
    """Tracks which courses each user has completed — prevents double-dipping."""
    __tablename__ = 'course_completion'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('login_store.id'), nullable=False)
    course_id  = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_id', name='uq_user_course'),
    )
class ColdStorageOwner(db.Model):
    __tablename__ = 'cold_storage_owner'

    id                      = db.Column(db.Integer, primary_key=True)
    user_id                 = db.Column(db.Integer, db.ForeignKey('login_store.id'), nullable=True)
    owner_name              = db.Column(db.String(100), nullable=False)
    phone                   = db.Column(db.String(15),  nullable=False)

    # Location
    village                 = db.Column(db.String(100), nullable=False)
    district                = db.Column(db.String(100), nullable=False)
    state                   = db.Column(db.String(100), nullable=False)

    # Storage Info
    total_capacity_tons     = db.Column(db.Float,       nullable=False)
    available_capacity_tons = db.Column(db.Float,       nullable=False)
    temperature_range       = db.Column(db.String(50),  nullable=False)  # e.g. "2°C - 8°C"
    supported_crops         = db.Column(db.String(200), nullable=False)  # e.g. "Potato, Onion"
    price_per_ton_per_month = db.Column(db.Float,       nullable=False)
    is_available            = db.Column(db.Boolean,     default=True)

    posted_at               = db.Column(db.DateTime,    default=datetime.utcnow)


class ColdStorageBooking(db.Model):
    __tablename__ = 'cold_storage_booking'

    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('login_store.id'), nullable=True)
    farmer_name      = db.Column(db.String(100), nullable=False)
    phone            = db.Column(db.String(15),  nullable=False)

    # What & Where
    crop_name        = db.Column(db.String(100), nullable=False)   # e.g. "Potato"
    quantity_tons    = db.Column(db.Float,       nullable=False)
    preferred_village = db.Column(db.String(100), nullable=False)
    preferred_district = db.Column(db.String(100), nullable=False)

    # Duration
    storage_from     = db.Column(db.Date,        nullable=False)
    storage_until    = db.Column(db.Date,        nullable=False)

    # Match status
    matched_storage_id = db.Column(db.Integer, db.ForeignKey('cold_storage_owner.id'), nullable=True)
    status           = db.Column(db.String(20),  default='pending')
    # 'pending' → 'matched' → 'completed'

    posted_at        = db.Column(db.DateTime,    default=datetime.utcnow)


with app.app_context():
    db.create_all()


from flask import session



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.Login()
    if form.validate_on_submit():
        Email = form.Email.data
        phone_number = form.phone_number.data
        password = form.password.data

        user = None

        if Email and Email.strip():
            user = LoginStore.query.filter_by(Email=Email, password=password).first()
        elif phone_number and phone_number.strip():
            user = LoginStore.query.filter_by(phone_number=phone_number, password=password).first()
        else:
            return render_template('login.html', form=form, error="Please provide either email or phone number")

        if user:
            session['user_id']      = user.id
            session['email'] = user.Email or user.phone_number # ✅ fixed typo
            session['phone_number'] = user.phone_number
            session['logged_in']    = True

            
            add_login_coin(user)

            return redirect(url_for('look'))
        else:
            return render_template('login.html', form=form, error="Invalid credentials")

    if form.errors:
        print("Form validation errors:", form.errors)

    return render_template('login.html', form=form)



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.Register()
    if form.validate_on_submit():
        name             = form.name.data
        Email            = form.Email.data
        phone_number     = form.phone_number.data
        password         = form.password.data
        confirm_password = form.confirm_password.data

        if Email:
            Email = Email.strip()
            if not Email:
                Email = None
        else:
            Email = None

        if phone_number:
            phone_number = phone_number.strip()

        if Email:
            existing_user_register = RegisterStore.query.filter_by(Email=Email).first()
            existing_user_login    = LoginStore.query.filter_by(Email=Email).first()
            if existing_user_register or existing_user_login:
                return render_template('register.html', form=form, error="Email already registered")

        if phone_number:
            existing_phone_register = RegisterStore.query.filter_by(Phone_number=phone_number).first()
            existing_phone_login    = LoginStore.query.filter_by(phone_number=phone_number).first()
            if existing_phone_register or existing_phone_login:
                return render_template('register.html', form=form, error="Phone number already registered")

        try:
            new_user_register = RegisterStore(
                name=name,
                Email=Email,
                Phone_number=phone_number,
                password=password,
                confirm_password=confirm_password
            )
            db.session.add(new_user_register)

            new_user_login = LoginStore(
                Email=Email,
                phone_number=phone_number,
                password=password,
                coins=0
            )
            db.session.add(new_user_login)
            db.session.commit()

            session['user_id']      = new_user_login.id
            session['email']        = new_user_login.Email or phone_number
            session['phone_number'] = phone_number
            session['logged_in']    = True

            sync_coins_to_session(new_user_login)
            add_coins(new_user_login, amount=1, reason="registration")

            flash('Registration successful!', 'success')
            return redirect(url_for('look'))

        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {str(e)}")
            return render_template('register.html', form=form, error=f"Registration failed: {str(e)}")

    if form.errors:
        print("Form validation errors:", form.errors)

    return render_template('register.html', form=form)
# Create tables
from datetime import datetime, timedelta

def add_coins(user, amount=1, reason="action"):
    user.coins += amount
    db.session.commit()
    session['coins'] = user.coins
    print(f"[COINS] +{amount} for '{reason}' | DB Total: {user.coins}")

def sync_coins_to_session(user):
    session['coins'] = user.coins

def get_coins():
    return session.get('coins', 0)

# ✅ NEW — only awards coin if 24 hours have passed since last login
def add_login_coin(user):
    if user is None:  # ✅ safety check
        return
        
    now = datetime.utcnow()

    if user.last_login is None:
        user.last_login = now
        add_coins(user, amount=1, reason="first login")

    elif now - user.last_login >= timedelta(hours=24):
        user.last_login = now
        add_coins(user, amount=1, reason="daily login")

    else:
        sync_coins_to_session(user)
        hours_left = 24 - (now - user.last_login).seconds // 3600
        print(f"[COINS] No coin — come back in ~{hours_left}h")

    db.session.commit()

model = None
scaler = None
crop_info = None
p_disease=None

def load_models():
    """Load the ML models and return status"""
    global model, scaler, crop_info, p_disease
    
    required_files = ["crop_model.pkl", "scaler.pkl", "crop_info.pkl"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        return {
            'status': 'error',
            'message': f"Missing required files: {', '.join(missing_files)}",
            'missing_files': missing_files
        }
    
    try:
        with open("crop_model.pkl", "rb") as f:
            model = pickle.load(f)
        with open("scaler.pkl", "rb") as f:
            scaler = pickle.load(f)
        with open("crop_info.pkl", "rb") as f:
            crop_info = pickle.load(f)
        
        return {
            'status': 'success',
            'message': 'All model files loaded successfully!'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Error loading files: {str(e)}"
        }







COURSES = {
    1: {"title": "Soil Health & NPK Basics",         "coins": 5},
    2: {"title": "Choosing the Right Crop",           "coins": 5},
    3: {"title": "Smart Irrigation",                  "coins": 5},
    4: {"title": "Identifying Crop Diseases",         "coins": 5},
    5: {"title": "Organic Farming",                   "coins": 5},
    6: {"title": "Mandi Prices & Market Timing",      "coins": 5},
    7: {"title": "AI & Drone Technology",             "coins": 5},
    8: {"title": "Kisan Credit & Loan Schemes",       "coins": 5},
}


# ── HELPER: get current logged-in user from DB ─────────────────────
def get_current_user():
    """Returns LoginStore object for the current session user, or None."""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return LoginStore.query.get(user_id)


# ── COURSES PAGE ───────────────────────────────────────────────────
@app.route('/courses')
def courses():
    if not session.get('logged_in'):
        flash('Please login to access courses.', 'warning')
        return redirect(url_for('login'))

    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    # Get list of completed course IDs for this user
    completed_rows = CourseCompletion.query.filter_by(user_id=user.id).all()
    completed_ids  = [row.course_id for row in completed_rows]

    # Sync coins to session (in case DB was updated elsewhere)
    sync_coins_to_session(user)

    return render_template(
        'courses.html',
        completed_courses=completed_ids,   # passed to Jinja → JS
        total_coins=user.coins,
    )


# ── COMPLETE COURSE (POST) ─────────────────────────────────────────
@app.route('/complete-course', methods=['POST'])
def complete_course():
    """
    Called by JS fetch() when user completes a course.
    Expects JSON:  { "course_id": <int> }
    Returns JSON:  { success, already_done, coins_earned, total_coins, ... }
    """
    if not session.get('logged_in'):
        return jsonify(success=False, error="Not logged in"), 401

    user = get_current_user()
    if not user:
        return jsonify(success=False, error="User not found"), 404

    # Parse request body
    data      = request.get_json(silent=True) or {}
    course_id = data.get('course_id')

    if not course_id or int(course_id) not in COURSES:
        return jsonify(success=False, error="Invalid course ID"), 400

    course_id = int(course_id)

    # ── Check already completed ────────────────────────────────────
    already = CourseCompletion.query.filter_by(
        user_id=user.id, course_id=course_id
    ).first()

    if already:
        return jsonify(
            success=True,
            already_done=True,
            coins_earned=0,
            total_coins=user.coins,
            message="Already completed"
        )

    # ── Award coins via your existing add_coins() helper ──────────
    coins_to_award = COURSES[course_id]['coins']

    try:
        # Save completion record
        record = CourseCompletion(user_id=user.id, course_id=course_id)
        db.session.add(record)

        # Add coins to DB + session using your existing function
        add_coins(user, amount=coins_to_award, reason=f"course_{course_id}")

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f"[COURSE ERROR] {e}")
        return jsonify(success=False, error="Database error"), 500

    return jsonify(
        success=True,
        already_done=False,
        coins_earned=coins_to_award,
        total_coins=user.coins,
        course_title=COURSES[course_id]['title'],
        message=f"+{coins_to_award} coins added!"
    )


# ── COIN HISTORY (optional — for dashboard) ────────────────────────
@app.route('/coin-history')
def coin_history():
    """Returns all completed courses + timestamps for the logged-in user."""
    if not session.get('logged_in'):
        return jsonify(error="Not logged in"), 401

    user = get_current_user()
    if not user:
        return jsonify(error="User not found"), 404

    rows = CourseCompletion.query.filter_by(user_id=user.id)\
                                 .order_by(CourseCompletion.completed_at.desc()).all()

    history = [
        {
            "course_id":    r.course_id,
            "course_title": COURSES.get(r.course_id, {}).get('title', 'Unknown'),
            "coins":        COURSES.get(r.course_id, {}).get('coins', 5),
            "completed_at": r.completed_at.strftime("%d %b %Y, %I:%M %p")
        }
        for r in rows
    ]

    return jsonify(
        success=True,
        history=history,
        total_coins=user.coins
    )




leaf_model = keras.models.load_model("leaf_model_fixed.h5", compile=False)
label = ['Apple___Apple_scab',
 'Apple___Black_rot',
 'Apple___Cedar_apple_rust',
 'Apple___healthy',
 'Background_without_leaves',
 'Blueberry___healthy',
 'Cherry___Powdery_mildew',
 'Cherry___healthy',
 'Corn___Cercospora_leaf_spot Gray_leaf_spot',
 'Corn___Common_rust',
 'Corn___Northern_Leaf_Blight',
 'Corn___healthy',
 'Grape___Black_rot',
 'Grape__Esca(Black_Measles)',
 'Grape__Leaf_blight(Isariopsis_Leaf_Spot)',
 'Grape___healthy',
 'Orange__Haunglongbing(Citrus_greening)',
 'Peach___Bacterial_spot',
 'Peach___healthy',
 'Pepper,bell__Bacterial_spot',
 'Pepper,bell__healthy',
 'Potato___Early_blight',
 'Potato___Late_blight',
 'Potato___healthy',
 'Raspberry___healthy',
 'Soybean___healthy',
 'Squash___Powdery_mildew',
 'Strawberry___Leaf_scorch',
 'Strawberry___healthy',
 'Tomato___Bacterial_spot',
 'Tomato___Early_blight',
 'Tomato___Late_blight',
 'Tomato___Leaf_Mold',
 'Tomato___Septoria_leaf_spot',
 'Tomato___Spider_mites Two-spotted_spider_mite',
 'Tomato___Target_Spot',
 'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
 'Tomato___Tomato_mosaic_virus',
 'Tomato___healthy']

# `plant_disease.json` loading removed since `label` array is equivalent

@app.route('/uploadimages/<path:filename>')
def uploaded_images(filename):
    return send_from_directory('./uploadimages', filename)

@app.route('/disease-detection', methods=['GET'])
def disease_detection():
    return render_template('disease.html')
    
def extract_features(image):
    image = keras.utils.load_img(image,target_size=(160,160))
    feature = keras.utils.img_to_array(image)
    feature = np.array([feature])
    return feature

def model_predict(image):
    img = extract_features(image)
    prediction = leaf_model.predict(img)
    prediction_label = label[prediction.argmax()]
    return prediction_label

import os

@app.route('/upload/', methods=['POST', 'GET'])
def uploadimage():
    if request.method == "POST":
        image = request.files['img']
        
        # ✅ Create the folder if it doesn't exist
        os.makedirs('uploadimages', exist_ok=True)
        
        temp_name = f"uploadimages/temp_{uuid.uuid4().hex}"
        save_path = f'{temp_name}_{image.filename}'
        image.save(save_path)
        
        prediction_label = model_predict(f'./{save_path}')
        prediction_data = get_disease_info(prediction_label)
        return render_template('disease.html', result=True, imagepath=f'/{save_path}', prediction=prediction_data)
    
    else:
        return redirect('/disease-detection')










































def get_weather_by_city(city_name):
    """Get current weather data by city name using WeatherAPI.com"""
    try:
        url = f"{WEATHER_BASE_URL}/current.json"
        params = {
            'key': WEATHER_API_KEY,
            'q': city_name,
            'aqi': 'yes'  # Include air quality data
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            'status': 'success',
            'data': {
                'city': data['location']['name'],
                'region': data['location']['region'],
                'country': data['location']['country'],
                'latitude': data['location']['lat'],
                'longitude': data['location']['lon'],
                'temperature': data['current']['temp_c'],
                'feels_like': data['current']['feelslike_c'],
                'humidity': data['current']['humidity'],
                'pressure': data['current']['pressure_mb'],
                'description': data['current']['condition']['text'],
                'icon': data['current']['condition']['icon'],
                'wind_speed': data['current']['wind_kph'] / 3.6,  # Convert to m/s
                'wind_direction': data['current']['wind_degree'],
                'wind_dir_text': data['current']['wind_dir'],
                'visibility': data['current']['vis_km'],
                'uv_index': data['current']['uv'],
                'cloud_cover': data['current']['cloud'],
                'last_updated': data['current']['last_updated'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'air_quality': data.get('current', {}).get('air_quality', {}) if 'air_quality' in data.get('current', {}) else None
            }
        }
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 400:
                return {
                    'status': 'error',
                    'message': f'City "{city_name}" not found or invalid request'
                }
            elif e.response.status_code == 401:
                return {
                    'status': 'error',
                    'message': 'Invalid API key'
                }
            elif e.response.status_code == 403:
                return {
                    'status': 'error',
                    'message': 'API key limit exceeded or access denied'
                }
        return {
            'status': 'error',
            'message': f'Weather API request failed: {str(e)}'
        }
    except KeyError as e:
        return {
            'status': 'error',
            'message': f'Invalid response format: {str(e)}'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Weather data error: {str(e)}'
        }

def get_weather_by_coordinates(lat, lon):
    """Get current weather data by coordinates using WeatherAPI.com"""
    try:
        url = f"{WEATHER_BASE_URL}/current.json"
        params = {
            'key': WEATHER_API_KEY,
            'q': f"{lat},{lon}",
            'aqi': 'yes'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            'status': 'success',
            'data': {
                'city': data['location']['name'],
                'region': data['location']['region'],
                'country': data['location']['country'],
                'latitude': data['location']['lat'],
                'longitude': data['location']['lon'],
                'temperature': data['current']['temp_c'],
                'feels_like': data['current']['feelslike_c'],
                'humidity': data['current']['humidity'],
                'pressure': data['current']['pressure_mb'],
                'description': data['current']['condition']['text'],
                'icon': data['current']['condition']['icon'],
                'wind_speed': data['current']['wind_kph'] / 3.6,  # Convert to m/s
                'wind_direction': data['current']['wind_degree'],
                'wind_dir_text': data['current']['wind_dir'],
                'visibility': data['current']['vis_km'],
                'uv_index': data['current']['uv'],
                'cloud_cover': data['current']['cloud'],
                'coordinates': {'lat': lat, 'lon': lon},
                'last_updated': data['current']['last_updated'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'air_quality': data.get('current', {}).get('air_quality', {}) if 'air_quality' in data.get('current', {}) else None
            }
        }
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 400:
                return {
                    'status': 'error',
                    'message': 'Invalid coordinates provided'
                }
            elif e.response.status_code == 401:
                return {
                    'status': 'error',
                    'message': 'Invalid API key'
                }
        return {
            'status': 'error',
            'message': f'Weather API request failed: {str(e)}'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Weather data error: {str(e)}'
        }

def get_weather_forecast(city_name, days=5):
    """Get weather forecast for specified days using WeatherAPI.com"""
    try:
        url = f"{WEATHER_BASE_URL}/forecast.json"
        params = {
            'key': WEATHER_API_KEY,
            'q': city_name,
            'days': min(days, 10),  # WeatherAPI supports up to 10 days
            'aqi': 'no',
            'alerts': 'no'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Process forecast data
        forecasts = []
        
        for day_data in data['forecast']['forecastday']:
            day = day_data['day']
            forecasts.append({
                'date': day_data['date'],
                'day': datetime.strptime(day_data['date'], '%Y-%m-%d').strftime('%A'),
                'temperature': {
                    'min': day['mintemp_c'],
                    'max': day['maxtemp_c'],
                    'avg': day['avgtemp_c']
                },
                'humidity': day['avghumidity'],
                'description': day['condition']['text'],
                'icon': day['condition']['icon'],
                'wind_speed': day['maxwind_kph'] / 3.6,  # Convert to m/s
                'precipitation': day['totalprecip_mm'],
                'chance_of_rain': day['daily_chance_of_rain'],
                'chance_of_snow': day['daily_chance_of_snow'],
                'uv_index': day['uv'],
                'sunrise': day_data['astro']['sunrise'],
                'sunset': day_data['astro']['sunset']
            })
        
        return {
            'status': 'success',
            'data': {
                'city': data['location']['name'],
                'region': data['location']['region'],
                'country': data['location']['country'],
                'forecasts': forecasts
            }
        }
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 400:
                return {
                    'status': 'error',
                    'message': f'City "{city_name}" not found or invalid request'
                }
            elif e.response.status_code == 401:
                return {
                    'status': 'error',
                    'message': 'Invalid API key'
                }
        return {
            'status': 'error',
            'message': f'Forecast API request failed: {str(e)}'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Forecast data error: {str(e)}'
        }

def get_agricultural_weather_insights(weather_data):
    """Generate agricultural insights based on weather data"""
    if weather_data['status'] != 'success':
        return {'status': 'error', 'message': 'Invalid weather data'}
    
    data = weather_data['data']
    insights = []
    alerts = []
    
    # Temperature insights
    temp = data['temperature']
    if temp < 5:
        alerts.append({
            'level': 'warning',
            'message': 'Low temperature alert: Risk of frost damage to crops'
        })
        insights.append('Consider protecting sensitive crops from frost')
    elif temp > 35:
        alerts.append({
            'level': 'warning',
            'message': 'High temperature alert: Heat stress risk for crops'
        })
        insights.append('Increase irrigation and provide shade for sensitive crops')
    elif 20 <= temp <= 30:
        insights.append('Optimal temperature range for most crop growth')
    
    # Humidity insights
    humidity = data['humidity']
    if humidity > 80:
        alerts.append({
            'level': 'caution',
            'message': 'High humidity: Increased risk of fungal diseases'
        })
        insights.append('Monitor crops for signs of fungal infections')
    elif humidity < 30:
        alerts.append({
            'level': 'caution',
            'message': 'Low humidity: Plants may experience water stress'
        })
        insights.append('Increase irrigation frequency')
    
    # Wind insights
    wind_speed = data.get('wind_speed', 0)
    if wind_speed > 10:  # m/s
        alerts.append({
            'level': 'warning',
            'message': 'Strong winds: Risk of physical damage to crops'
        })
        insights.append('Provide windbreaks for vulnerable crops')
    
    # UV Index insights
    uv_index = data.get('uv_index', 0)
    if uv_index > 8:
        alerts.append({
            'level': 'caution',
            'message': 'Very high UV index: Consider crop protection'
        })
        insights.append('High UV may benefit some crops but can stress others')
    
    # Cloud cover insights
    cloud_cover = data.get('cloud_cover', 50)
    if cloud_cover < 20:
        insights.append('Clear skies - excellent for photosynthesis')
    elif cloud_cover > 80:
        insights.append('Heavy cloud cover - reduced light for crops')
    
    # General farming recommendations
    recommendations = []
    description_lower = data['description'].lower()
    
    if any(word in description_lower for word in ['rain', 'drizzle', 'shower']):
        recommendations.append('Good day for transplanting - soil moisture is adequate')
        recommendations.append('Postpone pesticide/fertilizer application')
        recommendations.append('Check drainage systems in fields')
    elif any(word in description_lower for word in ['clear', 'sun', 'fair']):
        recommendations.append('Excellent day for harvesting and field work')
        recommendations.append('Good conditions for pesticide application')
        recommendations.append('Ideal for drying harvested crops')
    elif 'fog' in description_lower or 'mist' in description_lower:
        recommendations.append('Limited visibility - exercise caution during field work')
        recommendations.append('High moisture - monitor for disease development')
    
    # Air quality recommendations (if available)
    if data.get('air_quality'):
        aqi_data = data['air_quality']
        if 'co' in aqi_data and aqi_data['co'] > 10:
            recommendations.append('Poor air quality - avoid burning crop residue')
    
    return {
        'status': 'success',
        'insights': insights,
        'alerts': alerts,
        'recommendations': recommendations,
        'farming_conditions': {
            'field_work': 'Good' if wind_speed < 8 and 'rain' not in description_lower else 'Poor',
            'irrigation_need': 'High' if temp > 30 or humidity < 40 else 'Low' if temp < 20 and humidity > 60 else 'Medium',
            'pest_risk': 'High' if humidity > 70 and 20 < temp < 30 else 'Low',
            'uv_protection_needed': 'Yes' if uv_index > 7 else 'No'
        }
    }

def validate_input_data(data):
    """Validate input parameters"""
    required_params = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    
    for param in required_params:
        if param not in data:
            return False, f"Missing parameter: {param}"
    
    # Validate ranges
    validations = {
        'N': (0, 200),
        'P': (0, 200),
        'K': (0, 200),
        'temperature': (0, 50),
        'humidity': (0, 100),
        'ph': (0, 14),
        'rainfall': (0, 300)
    }
    
    for param, (min_val, max_val) in validations.items():
        try:
            value = float(data[param])
            if not (min_val <= value <= max_val):
                return False, f"{param} must be between {min_val} and {max_val}"
        except (ValueError, TypeError):
            return False, f"{param} must be a valid number"
    
    return True, "Valid"



class TaskGenerator:
    """Generate farm tasks based on inputs"""
    
    def __init__(self, farm_info, ml_predictions, weather_data, current_date):
        self.farm_info = farm_info
        self.ml_predictions = ml_predictions
        self.weather_data = weather_data
        self.current_date = current_date
        self.today_tasks = []
        self.weekly_tasks = []
    
    def check_rainfall_next_days(self, days=2):
        total_rainfall = 0
        for i in range(min(days, len(self.weather_data))):
            total_rainfall += self.weather_data[i].get('rainfall', 0)
        return total_rainfall
    
    def check_extreme_temperature(self):
        for day in self.weather_data[:3]:
            if day.get('temp_max', 0) > 40 or day.get('temp_min', 0) < 5:
                return True
        return False
    
    def get_date_offset(self, days):
        target_date = datetime.now() + timedelta(days=days)
        return target_date.strftime("%Y-%m-%d")

    def generate_irrigation_tasks(self):
        irrigation_urgency = self.ml_predictions.get('irrigation_urgency', 0.5)
        rainfall_next_2days = self.check_rainfall_next_days(2)
        if irrigation_urgency >= 0.7 and rainfall_next_2days < 5:
            self.today_tasks.append({
                "task_name": f"Irrigate {self.farm_info.get('crop_type', 'Crop')} Field",
                "priority": "High",
                "deadline": self.current_date,
                "reason": f"Soil moisture critically low ({int(irrigation_urgency * 100)}% urgency), no rain in 2 days",
                "risk_if_delayed": "Severe crop stress, wilting, reduced yield by 15-30%"
            })
        elif irrigation_urgency >= 0.7 and rainfall_next_2days >= 5:
            self.today_tasks.append({
                "task_name": "Monitor Soil Moisture",
                "priority": "Medium",
                "deadline": self.current_date,
                "reason": f"High irrigation urgency but {rainfall_next_2days}mm rainfall expected soon",
                "risk_if_delayed": "May still need irrigation if rain is insufficient"
            })
        elif irrigation_urgency >= 0.4 and rainfall_next_2days < 3:
            self.weekly_tasks.append({
                "task_name": f"Schedule Irrigation for {self.farm_info.get('crop_type', 'Crop')}",
                "priority": "Medium",
                "deadline": self.get_date_offset(2),
                "reason": "Moderate soil moisture depletion expected within 2-3 days",
                "risk_if_delayed": "Crop stress during critical growth stage"
            })

    def generate_labor_tasks(self):
        labor_demand = self.ml_predictions.get('labor_demand', 0.5)
        available_labor = self.farm_info.get('available_labor', 5)
        crop_stage = self.farm_info.get('crop_stage', '').lower()
        required_labor = int(labor_demand * 10)
        labor_gap = max(0, required_labor - available_labor)
        if labor_gap > 3 and 'harvest' in crop_stage:
            self.today_tasks.append({
                "task_name": "Arrange Additional Harvest Labor Urgently",
                "priority": "High",
                "deadline": self.current_date,
                "reason": f"Harvest needs {required_labor} workers, only {available_labor} available",
                "risk_if_delayed": "Delayed harvest, over-ripening, 20-40% crop loss"
            })
        elif labor_gap > 2:
            self.weekly_tasks.append({
                "task_name": f"Hire {labor_gap} Additional Workers",
                "priority": "High",
                "deadline": self.get_date_offset(3),
                "reason": f"Labor demand ({required_labor}) exceeds availability for {crop_stage}",
                "risk_if_delayed": "Delayed farm operations"
            })
        elif labor_demand >= 0.6:
            self.weekly_tasks.append({
                "task_name": "Confirm Labor Availability",
                "priority": "Medium",
                "deadline": self.get_date_offset(5),
                "reason": f"Moderate labor demand for {crop_stage} stage",
                "risk_if_delayed": "Last-minute labor shortage"
            })

    def generate_equipment_tasks(self):
        equipment_risk = self.ml_predictions.get('equipment_risk', 0.3)
        equipment_status = self.farm_info.get('equipment_status', '')
        if equipment_risk >= 0.7:
            self.today_tasks.append({
                "task_name": "Emergency Equipment Inspection",
                "priority": "High",
                "deadline": self.current_date,
                "reason": f"ML predicts {int(equipment_risk * 100)}% failure risk. Status: {equipment_status}",
                "risk_if_delayed": "Equipment breakdown during critical operations"
            })
        elif equipment_risk >= 0.5:
            self.weekly_tasks.append({
                "task_name": "Schedule Preventive Equipment Maintenance",
                "priority": "High",
                "deadline": self.get_date_offset(2),
                "reason": f"Moderate failure risk ({int(equipment_risk * 100)}%)",
                "risk_if_delayed": "Unexpected breakdowns"
            })
        elif 'repair' in equipment_status.lower() or 'needs' in equipment_status.lower():
            self.weekly_tasks.append({
                "task_name": "Repair Equipment",
                "priority": "Medium",
                "deadline": self.get_date_offset(4),
                "reason": f"Equipment needs maintenance: {equipment_status}",
                "risk_if_delayed": "Reduced operational capacity"
            })

    def generate_crop_stage_tasks(self):
        crop_stage = self.farm_info.get('crop_stage', '').lower()
        crop_type = self.farm_info.get('crop_type', 'crop')
        extreme_temp = self.check_extreme_temperature()
        if 'flowering' in crop_stage or 'reproductive' in crop_stage:
            self.weekly_tasks.append({
                "task_name": "Apply Flowering Stage Nutrients",
                "priority": "High",
                "deadline": self.get_date_offset(2),
                "reason": f"{crop_type.capitalize()} in flowering stage needs potassium and phosphorus",
                "risk_if_delayed": "Poor fruit/grain formation, yield loss 10-25%"
            })
            if extreme_temp:
                self.today_tasks.append({
                    "task_name": "Protect Flowering Crop from Temperature Stress",
                    "priority": "High",
                    "deadline": self.current_date,
                    "reason": "Extreme temperatures during sensitive flowering stage",
                    "risk_if_delayed": "Flower drop, pollination failure"
                })
        elif 'vegetative' in crop_stage or 'growth' in crop_stage:
            self.weekly_tasks.append({
                "task_name": "Apply Nitrogen Fertilizer",
                "priority": "Medium",
                "deadline": self.get_date_offset(3),
                "reason": f"{crop_type.capitalize()} in vegetative stage needs nitrogen",
                "risk_if_delayed": "Slower growth, weaker plants"
            })
        elif 'harvest' in crop_stage or 'mature' in crop_stage:
            self.today_tasks.append({
                "task_name": "Prepare Harvesting Equipment",
                "priority": "High",
                "deadline": self.current_date,
                "reason": f"{crop_type.capitalize()} ready for harvest soon",
                "risk_if_delayed": "Delayed harvest, quality degradation"
            })
            self.weekly_tasks.append({
                "task_name": "Arrange Storage/Transportation",
                "priority": "High",
                "deadline": self.get_date_offset(2),
                "reason": "Harvest approaching - need storage and logistics ready",
                "risk_if_delayed": "Post-harvest losses"
            })

    def generate_weather_based_tasks(self):
        if not self.weather_data:
            return
        heavy_rain_days = [i for i, day in enumerate(self.weather_data[:7]) if day.get('rainfall', 0) > 20]
        if heavy_rain_days and min(heavy_rain_days) <= 2:
            self.today_tasks.append({
                "task_name": "Prepare Drainage Systems",
                "priority": "High",
                "deadline": self.current_date,
                "reason": f"Heavy rainfall ({self.weather_data[min(heavy_rain_days)]['rainfall']}mm) expected in {min(heavy_rain_days)+1} days",
                "risk_if_delayed": "Waterlogging, root damage, fungal diseases"
            })
        total_weekly_rain = sum(day.get('rainfall', 0) for day in self.weather_data[:7])
        if total_weekly_rain < 5:
            self.weekly_tasks.append({
                "task_name": "Plan Water Conservation",
                "priority": "Medium",
                "deadline": self.get_date_offset(1),
                "reason": f"Only {total_weekly_rain}mm rainfall in next 7 days",
                "risk_if_delayed": "Water shortage during peak demand"
            })
        high_humidity_days = [d for d in self.weather_data[:5] if d.get('humidity', 0) > 85]
        if len(high_humidity_days) >= 3:
            self.weekly_tasks.append({
                "task_name": "Monitor for Fungal Diseases",
                "priority": "Medium",
                "deadline": self.get_date_offset(2),
                "reason": "High humidity (>85%) for multiple days - disease risk high",
                "risk_if_delayed": "Uncontrolled disease spread"
            })

    def generate_all_tasks(self):
        self.generate_irrigation_tasks()
        self.generate_labor_tasks()
        self.generate_equipment_tasks()
        self.generate_crop_stage_tasks()
        self.generate_weather_based_tasks()
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        self.today_tasks.sort(key=lambda x: priority_order.get(x['priority'], 3))
        self.weekly_tasks.sort(key=lambda x: priority_order.get(x['priority'], 3))
        return {
            "today_tasks": self.today_tasks,
            "weekly_tasks": self.weekly_tasks,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "farm_summary": {
                "crop": self.farm_info.get('crop_type'),
                "stage": self.farm_info.get('crop_stage'),
                "size": self.farm_info.get('farm_size')
            }
        }
    



@app.route('/farm-plan')
def farm_plan():
    """7-day farm operations plan page"""
    return render_template('7dayplan.html')

@app.route("/gamecourse")
def gamecourse():
    return render_template("gamecourse.html",)



@app.route('/get_farm_plan', methods=['POST'])
def get_farm_plan():
    """Generate farm operation plan (renamed from /get_plan to avoid conflicts)"""
    try:
        data = request.get_json()
        farm_info = data.get('farm_info', {})
        ml_predictions = data.get('ml_predictions', {})
        weather_data = data.get('weather_data', [])
        if not farm_info or not ml_predictions:
            return jsonify({"error": "Missing required fields: farm_info and ml_predictions"}), 400
        current_date = datetime.now().strftime("%Y-%m-%d")
        task_generator = TaskGenerator(farm_info, ml_predictions, weather_data, current_date)
        result = task_generator.generate_all_tasks()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Error processing request: {str(e)}"}), 500


@app.route('/api/farm-weather', methods=['GET'])
def farm_weather_forecast():
    """Dummy weather forecast for farm plan (renamed from /weather to avoid conflict)"""
    dummy_weather = [
        {"day": 0, "rainfall": 0,  "temp_max": 32, "temp_min": 18, "humidity": 65},
        {"day": 1, "rainfall": 0,  "temp_max": 33, "temp_min": 19, "humidity": 60},
        {"day": 2, "rainfall": 5,  "temp_max": 30, "temp_min": 17, "humidity": 75},
        {"day": 3, "rainfall": 12, "temp_max": 28, "temp_min": 16, "humidity": 80},
        {"day": 4, "rainfall": 3,  "temp_max": 31, "temp_min": 18, "humidity": 70},
        {"day": 5, "rainfall": 0,  "temp_max": 34, "temp_min": 20, "humidity": 58},
        {"day": 6, "rainfall": 0,  "temp_max": 35, "temp_min": 21, "humidity": 55}
    ]
    return jsonify({"weather_forecast": dummy_weather}), 200





# ============================================================
# COLD STORAGE ROUTES — paste into your existing app.py
# ============================================================
from forms import ColdStorageOwnerForm, ColdStorageBookingForm

@app.route('/cold-storage', methods=['GET', 'POST'])
def cold_storage_home():
    owner_form   = ColdStorageOwnerForm()
    booking_form = ColdStorageBookingForm()
    storages     = ColdStorageOwner.query.filter_by(is_available=True).all()
    bookings     = ColdStorageBooking.query.filter_by(user_id=session.get('user_id')).all()
    return render_template('cold_storage.html',
                           owner_form=owner_form,
                           booking_form=booking_form,
                           storages=storages,
                           bookings=bookings)


@app.route('/cold-storage/owner/add', methods=['POST'])
def cold_storage_owner_add():
    form = ColdStorageOwnerForm()
    if form.validate_on_submit():
        owner = ColdStorageOwner(
            user_id                 = session.get('user_id'),
            owner_name              = form.owner_name.data,
            phone                   = form.phone.data,
            village                 = form.village.data,
            district                = form.district.data,
            state                   = form.state.data,
            total_capacity_tons     = form.total_capacity_tons.data,
            available_capacity_tons = form.available_capacity_tons.data,
            temperature_range       = form.temperature_range.data,
            supported_crops         = form.supported_crops.data,
            price_per_ton_per_month = form.price_per_ton_per_month.data,
        )
        db.session.add(owner)
        db.session.commit()
        flash('✅ Cold storage listed successfully!', 'success')
    else:
        flash('❌ Please fix errors in the owner form.', 'danger')
    return redirect(url_for('cold_storage_home'))


@app.route('/cold-storage/book/add', methods=['POST'])
def cold_storage_book_add():
    form = ColdStorageBookingForm()
    if form.validate_on_submit():
        booking = ColdStorageBooking(
            user_id            = session.get('user_id'),
            farmer_name        = form.farmer_name.data,
            phone              = form.phone.data,
            crop_name          = form.crop_name.data,
            quantity_tons      = form.quantity_tons.data,
            preferred_village  = form.preferred_village.data,
            preferred_district = form.preferred_district.data,
            storage_from       = form.storage_from.data,
            storage_until      = form.storage_until.data,
        )
        # Auto-match by district + enough capacity
        match = ColdStorageOwner.query.filter_by(
            district     = form.preferred_district.data,
            is_available = True
        ).filter(
            ColdStorageOwner.available_capacity_tons >= form.quantity_tons.data
        ).first()

        if match:
            booking.matched_storage_id = match.id
            booking.status = 'matched'
            match.available_capacity_tons -= form.quantity_tons.data
            if match.available_capacity_tons <= 0:
                match.is_available = False
            flash(f'✅ Matched with {match.owner_name} in {match.village}!', 'success')
        else:
            flash('📋 Booking submitted! We will find a match soon.', 'info')

        db.session.add(booking)
        db.session.commit()
    else:
        flash('❌ Please fix errors in the booking form.', 'danger')
    return redirect(url_for('cold_storage_home'))


@app.route('/cold-storage/toggle/<int:owner_id>')
def toggle_cold_storage(owner_id):
    owner = ColdStorageOwner.query.get_or_404(owner_id)
    if owner.user_id != session.get('user_id'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('cold_storage_home'))
    owner.is_available = not owner.is_available
    db.session.commit()
    flash('Storage availability updated!', 'success')
    return redirect(url_for('cold_storage_home'))


















































@app.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

@app.route('/look')
def look():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return render_template('look.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    user = LoginStore.query.get(session['user_id'])
    
    if user is None:  # ✅ safety check
        session.clear()
        return redirect(url_for('login'))

    session['coins'] = user.coins
    session.modified = True

    now = datetime.utcnow()
    if user.last_login and (now - user.last_login) < timedelta(hours=24):
        remaining = timedelta(hours=24) - (now - user.last_login)
        hours   = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60
        next_coin = f"{hours}h {minutes}m"
    else:
        next_coin = "Available now!"

    user_data = {
        'email'     : user.Email or user.phone_number,
        'coins'     : user.coins,
        'next_coin' : next_coin
    }
    
    # Generate mock 30-day market price trend for Wheat and Rice
    import random
    from datetime import date
    
    today = date.today()
    dates_30 = [(today - timedelta(days=i)).strftime('%b %d') for i in range(29, -1, -1)]
    
    wheat_price = 2100
    rice_price = 2800
    wheat_prices = []
    rice_prices = []
    
    for _ in range(30):
        wheat_price += random.randint(-20, 25)
        rice_price += random.randint(-30, 35)
        wheat_prices.append(max(1500, wheat_price))
        rice_prices.append(max(2000, rice_price))
        
    market_data = {
        'labels': dates_30,
        'wheat': wheat_prices,
        'rice': rice_prices
    }
    
    # Generate mock 5-day weather trend
    dates_5 = [(today + timedelta(days=i)).strftime('%b %d') for i in range(5)]
    weather_data = {
        'labels': dates_5,
        'temp_max': [random.randint(30, 35) for _ in range(5)],
        'temp_min': [random.randint(20, 25) for _ in range(5)],
        'rainfall': [random.randint(0, 40) for _ in range(5)]
    }

    return render_template('dashboard.html', user=user_data, market_data=json.dumps(market_data), weather_data=json.dumps(weather_data))


# ── LIVE MAP ROUTE ───────────────────────────────────────────────
@app.route('/map')
def live_map():
    """Live Map page for Cold Storage and Renting Equipment"""
    # Generate some mock data around central India (Bhopal/Nagpur area) or let map auto-center
    mock_facilities = [
        # Odisha
        {"id": 1, "name": "Bhubaneswar Cold Storage Hub", "lat": 20.2961, "lng": 85.8245, "type": "storage", "capacity": "85%"},
        {"id": 2, "name": "Cuttack Agro Cold Chain", "lat": 20.4625, "lng": 85.8830, "type": "storage", "capacity": "60%"},
        {"id": 3, "name": "Puri Farmer Tractors (Rent)", "lat": 19.8135, "lng": 85.8312, "type": "rent", "equipment": "Tractors, Harvesters"},
        {"id": 4, "name": "Khurda Equipment Rentals", "lat": 20.1833, "lng": 85.6167, "type": "rent", "equipment": "Pumps, Sprayers"},
        {"id": 5, "name": "Rourkela Mega Cold Storage", "lat": 22.2604, "lng": 84.9240, "type": "storage", "capacity": "45%"},
        {"id": 6, "name": "Sambalpur Farming Gear", "lat": 21.4684, "lng": 83.9772, "type": "rent", "equipment": "Seed Drills, Plows"},
        {"id": 7, "name": "Berhampur Coastal Storage", "lat": 19.3150, "lng": 84.7941, "type": "storage", "capacity": "90%"},
        {"id": 8, "name": "Balasore Agri Implements", "lat": 21.4934, "lng": 86.9338, "type": "rent", "equipment": "Combine Harvesters"},
        
        # All over India
        {"id": 9, "name": "New Delhi Central Storage", "lat": 28.6139, "lng": 77.2090, "type": "storage", "capacity": "30%"},
        {"id": 10, "name": "Mumbai Port Cold Chain", "lat": 19.0760, "lng": 72.8777, "type": "storage", "capacity": "75%"},
        {"id": 11, "name": "Bangalore Tech-Agri Rentals", "lat": 12.9716, "lng": 77.5946, "type": "rent", "equipment": "Drones, Smart Sprayers"},
        {"id": 12, "name": "Chennai Produce Storage", "lat": 13.0827, "lng": 80.2707, "type": "storage", "capacity": "55%"},
        {"id": 13, "name": "Kolkata Eastern Cold Hub", "lat": 22.5726, "lng": 88.3639, "type": "storage", "capacity": "82%"},
        {"id": 14, "name": "Hyderabad Farm Equipment", "lat": 17.3850, "lng": 78.4867, "type": "rent", "equipment": "Tractors, Rotavators"},
        {"id": 15, "name": "Ahmedabad Gujrat Storage", "lat": 23.0225, "lng": 72.5714, "type": "storage", "capacity": "20%"},
        {"id": 16, "name": "Pune Western Ghat Rentals", "lat": 18.5204, "lng": 73.8567, "type": "rent", "equipment": "Tillers, Cultivators"},
        {"id": 17, "name": "Jaipur Desert Agro Storage", "lat": 26.9124, "lng": 75.7873, "type": "storage", "capacity": "68%"},
        {"id": 18, "name": "Lucknow UP Farm Tools", "lat": 26.8467, "lng": 80.9462, "type": "rent", "equipment": "Pumps, Diggers"},
        {"id": 19, "name": "Patna Bihar Cold Chain", "lat": 25.5941, "lng": 85.1376, "type": "storage", "capacity": "40%"}
    ]
    return render_template('map.html', facilities=json.dumps(mock_facilities))


# ── COMMUNITY LEADERBOARD ROUTE ───────────────────────────────────────────────
@app.route('/leaderboard')
def leaderboard():
    """Top farmers by earned coins/credits"""
    top_users = LoginStore.query.order_by(LoginStore.coins.desc()).limit(10).all()
    # Handle case where db might be empty
    if not top_users:
        # Mock users for demonstration if DB is empty
        mock_users = [
            type('MockUser', (object,), {'name': 'Ankit Biswal', 'coins': 500}),
            type('MockUser', (object,), {'name': 'Ramesh Kumar', 'coins': 320}),
            type('MockUser', (object,), {'name': 'Sunita Devi', 'coins': 150}),
            type('MockUser', (object,), {'name': 'Rahul Sharma', 'coins': 45})
        ]
        top_users = [u() for u in mock_users]
    
    return render_template('leaderboard.html', top_users=top_users)


# ── MULTILINGUAL VOICE ASSISTANT ROUTE (GROQ) ─────────────────────────────────
@app.route('/voice-chat', methods=['POST'])
def voice_chat():
    """Endpoint for the browser-based voice assistant to get AI responses"""
    if not groq_client:
        return jsonify({"error": "Voice AI is currently offline. Missing API Key."}), 503

    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400

    user_message = data['message']
    
    # Simple system prompt to ensure concise and helpful farming advice
    system_prompt = (
        "You are Krushi Sakha, a highly intelligent and friendly AI assistant for Indian farmers. "
        "Keep your answers extremely concise (1-2 sentences max) because they will be read aloud by TTS. "
        "Answer the farmer's question related to agriculture, weather, crops, or market prices clearly."
    )

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.4,
            max_tokens=150
        )
        ai_text = response.choices[0].message.content.strip()
        return jsonify({"reply": ai_text})
        
    except Exception as e:
        print(f"Voice Assistant Error: {e}")
        return jsonify({"error": "Sorry, I am having trouble connecting to my brain right now."}), 500


# ── SMS ALERTS (TWILIO + BACKGROUND THREAD) ───────────────────────────────────

def send_sms_alert(to_phone, message_body):
    """Sends an SMS using Twilio, or mocks it if credentials are not configured."""
    if not to_phone: return False
    
    # Ensure phone number has country code for Twilio
    if not to_phone.startswith('+'):
        to_phone = '+91' + to_phone[-10:] if len(to_phone) >= 10 else to_phone

    if twilio_client and TWILIO_PHONE_NUMBER:
        try:
            message = twilio_client.messages.create(
                body=message_body,
                from_=TWILIO_PHONE_NUMBER,
                to=to_phone
            )
            print(f"[SMS SENT] To {to_phone}: {message_body}")
            return True
        except Exception as e:
            print(f"[TWILIO ERROR] {e}")
            return False
    else:
        print(f"[MOCK SMS] To {to_phone}: {message_body}")
        return True

@app.route('/subscribe-alerts', methods=['POST'])
def subscribe_alerts():
    """Allows a farmer to subscribe to daily market & weather alerts"""
    try:
        user_email = session.get('email')
        if not user_email:
            return jsonify({"error": "Please login to subscribe to alerts."}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload provided."}), 400
            
        phone = data.get('phone')
        if not phone or len(phone) < 10:
            return jsonify({"error": "Invalid phone number."}), 400
            
        # Check if another user already registered this phone number
        existing_phone = LoginStore.query.filter_by(phone_number=phone).first()
        user = LoginStore.query.filter_by(Email=user_email).first()
        
        if existing_phone and existing_phone.id != user.id:
            return jsonify({"error": "This phone number is already registered to another account."}), 400
            
        # Save to database
        if user:
            user.phone_number = phone
            db.session.commit()
            
        # Send welcome message
        welcome_msg = "🌾 Krushi Sakha: You are successfully subscribed to Daily Smart Alerts for Weather & Market Prices!"
        success = send_sms_alert(phone, welcome_msg)
        
        if success:
            return jsonify({"success": "Subscribed successfully! You will receive a confirmation SMS shortly."})
        else:
            return jsonify({"error": "Failed to send SMS. Please check your number."}), 500
    except Exception as e:
        print(f"Subscribe Alert Error: {e}")
        db.session.rollback() # Important to rollback the broken transaction
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

# Background thread logic for scheduled alerts
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

def trigger_daily_alerts():
    """Scheduled task to send alerts to all users"""
    print("[SCHEDULER] Running daily smart alerts check...")
    with app.app_context():
        # Get users with phone numbers
        users = LoginStore.query.filter(LoginStore.phone_number != None).all()
        for user in users:
            # Generate a dynamic AI or mock alert
            alert_msg = f"🌾 KrushiSakha Alert for {user.Email() if hasattr(user, 'Email') else 'Farmer'}:\n📍 Today's Weather: Sunny, 32°C.\n📈 Market: Wheat price up by ₹40/qtl in your local mandi. Good time to sell!"
            send_sms_alert(user.phone_number, alert_msg)

# Schedule for 8:00 AM every day (Testing: comment out for instant tests if needed)
schedule.every().day.at("08:00").do(trigger_daily_alerts)

# Start the background thread for scheduler
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

























# Fixed Backend Code

@app.route("/appoinment", methods=['GET', 'POST'])  # Added POST method
def appoinment():
    form = forms.FarmerForm()  # Fixed: form-= should be form =
    if form.validate_on_submit():
        name = form.name.data
        Email = form.Email.data
        phone = form.phone.data
        address = form.address.data
        state = form.state.data
        city = form.city.data
        zip_code = form.zip.data
        farm_size = form.farm_size.data
        crop_types = form.crop_type.data
        irrigation_methods = form.irrigation_methods.data
        soil_type = form.soil_type.data
        experience_level = form.experience_level.data
        
        try:
            # Save to database
            new_farmer = Farmerstore(
                name=name,
                Email=Email,
                phone=str(phone),  # Convert to string for database storage
                address=address,
                state=state,
                city=city,
                zip_code=str(zip_code),  # Convert to string for database storage
                farm_size=farm_size,
                crop_types=crop_types,
                irrigation_methods=irrigation_methods,
                soil_type=soil_type,
                experience_level=experience_level
            )
            db.session.add(new_farmer)
            db.session.commit()
            
            # Trigger phone call here
            trigger_phone_call(phone, name)
            
            return render_template('appoinment.html', form=form, success=True)
        
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while saving your information. Please try again.', 'error')
            return render_template('appoinment.html', form=form)
    
    return render_template('appoinment.html', title="Appointment", form=form)

# Function to trigger phone call (you'll need to implement this with a service like Twilio)
def trigger_phone_call(farmer_phone, farmer_name):
    """
    This function should implement the actual phone call logic.
    You can use Twilio, VoIP services, or other telephony APIs.
    """
    try:
        # Example using Twilio (you'll need to install twilio package and set up credentials)
        # from twilio.rest import Client
        # 
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "placeholder_sid")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "placeholder_token")
        client = Client(account_sid, auth_token)
        
        call = client.calls.create(
            to='+917846917002',  # The number to call
            from_='+16516154405',  # Your Twilio number
            twiml=f'<Response><Say>New farmer consultation request from {farmer_name}. Phone: {farmer_phone}</Say></Response>'
        )
        
        # For now, just log the call request
        print(f"Phone call triggered to 7846917002 for farmer: {farmer_name}, Phone: {farmer_phone}")
        
    except Exception as e:
        print(f"Error triggering phone call: {e}")

# Alternative route to handle AJAX phone call requests
@app.route("/trigger-phone-call", methods=['POST'])
def trigger_phone_call_ajax():
    """Route to handle phone call requests via AJAX"""
    try:
        data = request.get_json()
        to_number = data.get('to')
        farmer_phone = data.get('farmerPhone')
        farmer_name = data.get('farmerName')
        
        # Call your phone service here
        trigger_phone_call(farmer_phone, farmer_name)
        
        return jsonify({'status': 'success', 'message': 'Phone call triggered successfully'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500




















@app.route("/about")
def about():
    """About page route"""
    return render_template('about.html')

@app.route("/popup")
def popup():
    """Popup page route"""
    return render_template('popup.html',title="schemes")

@app.route("/mp")
def mp():
    """Market price page route"""
    return render_template('mp.html',title="Market Price")

@app.route("/ac")
def ac():
    """Agricultural calendar page route"""
    return render_template('ac.html',title="Agricultural Calendar")

@app.route("/marketprices")
def marketprice():
    """Market price page route"""
    return render_template('marketprices.html',title="Market Price")

@app.route("/services")
def services():
    """Services page route"""
    return render_template('services.html',title="Services")

@app.route("/ftalk")
def ftalk():
    """farmer talk page route"""
    return render_template('ftalk.html',title="farmer Talk")



@app.route("/rental", methods=['GET', 'POST'])
def rental():
    form = forms.rentform()
   
    location_success = request.args.get('location_success', False)
   
    if form.validate_on_submit():
        name = form.name.data
        email = form.Email.data
        phone = form.phone.data
        address = form.address.data
        state = form.state.data
        city = form.city.data
        zip_code = form.zip.data
        rentdate = form.rentdate.data
        return_date = form.return_date.data
       
        new_rent = RentStore(
            name=name,
            email=email,
            phone=phone,
            address=address,
            state=state,
            city=city,
            zip_code=zip_code,
            rentdate=str(rentdate),
            return_date=str(return_date)
        )
       
        try:
            db.session.add(new_rent)
            db.session.commit()
            return jsonify({'status': 'success'}), 200
        except Exception as e:
            db.session.rollback()
            print(f"Error saving order: {e}")
            return jsonify({'status': 'error'}), 500
   
    return render_template('rent.html', title="rent", form=form, location_success=location_success)


@app.route("/order", methods=['GET', 'POST'])
def order():
    form = forms.orderform()
    
    # Check for location success query parameter
    location_success = request.args.get('location_success', False)
    
    if form.validate_on_submit():
        name = form.name.data
        email = form.Email.data
        phone = form.phone.data
        address = form.address.data
        state = form.state.data
        city = form.city.data
        zip_code = form.zip.data
        
        # Create new order instance
        new_order = OrderStore(
            name=name,
            email=email,
            phone=phone,
            address=address,
            state=state,
            city=city,
            zip_code=zip_code
        )
        
        # Add to database
        try:
            db.session.add(new_order)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error saving order: {e}")  # For debugging
        
        return render_template('order.html', form=form, success=True, title="Order")
    
    return render_template('order.html', title="Order", form=form, location_success=location_success)

@app.route("/shop")
def shop():
    """Shop page route"""
    return render_template('shop.html',title="Shop")



@app.route("/jb", methods=['GET', 'POST'])
def jb():
    """Job board page route"""
    form =forms.WorkerForm()
    
    if form.validate_on_submit():
        # Extract form data
        name = form.name.data
        location = form.location.data
        phone = form.phone.data
        availability = form.availability.data
        budget = form.budget.data
        additional_info = form.additional_info.data
        skills = form.skills.data
        
        flash(f'Form submitted successfully for {name}!', 'success')
        return redirect(url_for('jb'))
    
    return render_template('jb.html', title="Job Board", form=form)



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/predict')
def predict_page():
    return render_template('predict.html', title="Crop Prediction")

@app.route("/guide")
def guide():
    """Guide page route"""
    return render_template('guide.html',title="Guide")

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    """Contact page route"""
    form = forms.Contact()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data
        
        # Save to database
        new_user = User(name=name, email=email, message=message)
        db.session.add(new_user)
        db.session.commit()
        
        return render_template('contact.html', form=form, success=True)
    
    return render_template('contact.html', form=form)


@app.route('/farming-calendar')
def farming_calendar():
    """Farming calendar page route"""
    return render_template('fc.html', title="Farming Calendar")


@app.route('/weather')
def weather():
    """Weather page route - Enhanced with API integration"""
    # You can get default weather for a specific city or let frontend handle it
    default_city = request.args.get('city', 'New Delhi')  # Default to New Delhi for Indian agriculture
    
    weather_data = get_weather_by_city(default_city)
    insights_data = None
    
    if weather_data['status'] == 'success':
        insights_data = get_agricultural_weather_insights(weather_data)
    
    return render_template('weather.html', 
                         title="Weather", 
                         weather_data=weather_data,
                         insights_data=insights_data,
                         default_city=default_city)

# Weather API Routes
@app.route('/api/weather/current', methods=['GET'])
def api_current_weather():
    """API endpoint to get current weather by city or coordinates"""
    city = request.args.get('city')
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    
    if city:
        weather_data = get_weather_by_city(city)
    elif lat and lon:
        try:
            lat = float(lat)
            lon = float(lon)
            weather_data = get_weather_by_coordinates(lat, lon)
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Invalid coordinates'}), 400
    else:
        return jsonify({'status': 'error', 'message': 'City name or coordinates required'}), 400
    
    if weather_data['status'] == 'error':
        return jsonify(weather_data), 400
    
    # Add agricultural insights
    insights = get_agricultural_weather_insights(weather_data)
    weather_data['agricultural_insights'] = insights
    
    return jsonify(weather_data)

@app.route('/api/weather/debug')
def debug_weather_api():
    """Debug route to test API key and connection with WeatherAPI.com"""
    try:
        # Test API key with a simple request
        test_url = f"{WEATHER_BASE_URL}/current.json"
        params = {
            'key': WEATHER_API_KEY,
            'q': 'London'
        }
        
        response = requests.get(test_url, params=params, timeout=10)
        
        return jsonify({
            'status_code': response.status_code,
            'api_key_length': len(WEATHER_API_KEY),
            'api_key_first_8': WEATHER_API_KEY[:8] + '...',
            'url': test_url,
            'response_text': response.text[:500] if response.text else 'No response text',
            'headers': dict(response.headers),
            'error': None
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'error',
            'error_type': 'RequestException',
            'error_message': str(e),
            'api_key_length': len(WEATHER_API_KEY),
            'api_key_first_8': WEATHER_API_KEY[:8] + '...'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error_type': 'Exception',
            'error_message': str(e)
        })

@app.route('/api/weather/test-connection')
def test_weather_connection():
    """Test basic internet connectivity and WeatherAPI.com"""
    try:
        # Test basic connectivity
        response = requests.get('https://httpbin.org/status/200', timeout=5)
        internet_ok = response.status_code == 200
        
        # Test WeatherAPI.com connectivity
        response = requests.get('https://api.weatherapi.com/v1/current.json?key=test&q=London', timeout=5)
        weatherapi_reachable = True
        
        return jsonify({
            'internet_connection': internet_ok,
            'weatherapi_reachable': weatherapi_reachable,
            'weatherapi_response_code': response.status_code,
            'weatherapi_response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:200]
        })
        
    except Exception as e:
        return jsonify({
            'internet_connection': False,
            'error': str(e)
        })

@app.route('/api/weather/forecast', methods=['GET'])
def api_weather_forecast():
    """API endpoint to get weather forecast"""
    city = request.args.get('city')
    days = request.args.get('days', 5)
    
    if not city:
        return jsonify({'status': 'error', 'message': 'City name required'}), 400
    
    try:
        days = int(days)
        if days < 1 or days > 10:
            days = 5
    except ValueError:
        days = 5
    
    forecast_data = get_weather_forecast(city, days)
    return jsonify(forecast_data)

@app.route('/api/weather/agricultural-insights', methods=['POST'])
def api_agricultural_insights():
    """API endpoint to get agricultural insights from weather data"""
    try:
        weather_data = request.get_json()
        if not weather_data:
            return jsonify({'status': 'error', 'message': 'Weather data required'}), 400
        
        insights = get_agricultural_weather_insights(weather_data)
        return jsonify(insights)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error generating insights: {str(e)}'}), 500

@app.route('/api/weather/crop-conditions', methods=['GET'])
def api_crop_conditions():
    """API endpoint to get current crop growing conditions based on weather"""
    city = request.args.get('city', 'New Delhi')
    
    weather_data = get_weather_by_city(city)
    if weather_data['status'] == 'error':
        return jsonify(weather_data), 400
    
    insights = get_agricultural_weather_insights(weather_data)
    
    # Combine weather and crop prediction if soil data is provided
    soil_data = request.args.to_dict()
    crop_recommendation = None
    
    # Check if soil parameters are provided
    if all(param in soil_data for param in ['N', 'P', 'K', 'ph']):
        try:
            # Use weather data to enhance soil data
            enhanced_soil_data = soil_data.copy()
            enhanced_soil_data['temperature'] = weather_data['data']['temperature']
            enhanced_soil_data['humidity'] = weather_data['data']['humidity']
            enhanced_soil_data['rainfall'] = 0  # Assume no recent rainfall, can be enhanced
            
            # Validate and get crop recommendation
            is_valid, message = validate_input_data(enhanced_soil_data)
            if is_valid and model is not None:
                # Prepare input for crop prediction
                N = float(enhanced_soil_data['N'])
                P = float(enhanced_soil_data['P'])
                K = float(enhanced_soil_data['K'])
                temperature = float(enhanced_soil_data['temperature'])
                humidity = float(enhanced_soil_data['humidity'])
                ph = float(enhanced_soil_data['ph'])
                rainfall = float(enhanced_soil_data['rainfall'])
                
                input_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
                input_scaled = scaler.transform(input_data)
                
                probabilities = model.predict_proba(input_scaled)[0]
                top_crop_idx = np.argmax(probabilities)
                top_crop = model.classes_[top_crop_idx]
                confidence = round(probabilities[top_crop_idx] * 100, 2)
                
                crop_recommendation = {
                    'recommended_crop': top_crop.capitalize(),
                    'confidence': confidence,
                    'suitable_for_current_weather': confidence > 70
                }
        except Exception as e:
            crop_recommendation = {'error': f'Could not generate crop recommendation: {str(e)}'}
    
    return jsonify({
        'status': 'success',
        'weather': weather_data['data'],
        'agricultural_insights': insights,
        'crop_recommendation': crop_recommendation,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/status')
def api_status():
    """API endpoint to check model loading status"""
    model_status = load_models()
    return jsonify(model_status)




@app.route('/marketprice')
def market_price():
    """Market price page route"""
    return render_template('marketprice.html',title="Market Price")


@app.route('/loan')
def loan():
    """Loan page route"""
    return render_template('loan.html',title="Loan")

    
@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Handles chatbot messages using Groq LLaMA3"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
        
    try:
        # Construct system prompt for the farming context
        system_prompt = (
            "You are Krushi Sakha, a highly knowledgeable and friendly agricultural AI assistant in India. "
            "Your goal is to provide accurate, easy-to-understand advice on farming, "
            "crops, soil preparation, fertilizers, diseases, and government schemes. "
            "Keep your answers concise, practical, and highly relevant to Indian agriculture. "
            "Use a polite and encouraging tone."
        )

        # Call Groq API
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            model="llama3-8b-8192",
            temperature=0.7,
            max_tokens=500,
        )
        
        reply_text = chat_completion.choices[0].message.content
        return jsonify({'reply': reply_text})
        
    except Exception as e:
        app.logger.error(f"Groq API Error: {str(e)}")
        fallback_reply = "I apologize, but my advanced AI servers are currently taking a quick break. Please try asking your question again in a few moments!"
        return jsonify({'reply': fallback_reply})

@app.route('/chatbot')
def chatbot():
    """Custom in-app AI Chatbot route"""
    if not session.get('logged_in'):
        flash('Please login to use the AI Chatbot.', 'warning')
        return redirect(url_for('login'))
    return render_template('chat.html')

@app.route('/games')
def games():
    if not session.get('logged_in'):
        flash('Please login to play games.', 'warning')
        return redirect(url_for('login'))
    return render_template('games.html')


@app.route('/add-game-coins', methods=['POST'])
def add_game_coins():
    """Called by JS when player wins coins in a game."""
    if not session.get('logged_in'):
        return jsonify(success=False, error="Not logged in"), 401

    user = LoginStore.query.get(session.get('user_id'))
    if not user:
        return jsonify(success=False, error="User not found"), 404

    data  = request.get_json(silent=True) or {}
    coins = int(data.get('coins', 0))

    if coins <= 0 or coins > 10:   # sanity check — max 10 per call
        return jsonify(success=False, error="Invalid coin amount"), 400

    add_coins(user, amount=coins, reason="game_win")  # uses your existing helper

    return jsonify(
        success=True,
        coins_added=coins,
        total_coins=user.coins
    )





































































































@app.route('/api/predict', methods=['POST'])
def predict_crop():
    """API endpoint for crop prediction"""
    try:
        # Check if models are loaded
        if model is None or scaler is None or crop_info is None:
            model_status = load_models()
            if model_status['status'] == 'error':
                return jsonify(model_status), 500
        
        # Get data from request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate input data
        is_valid, message = validate_input_data(data)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Extract parameters
        N = float(data['N'])
        P = float(data['P'])
        K = float(data['K'])
        temperature = float(data['temperature'])
        humidity = float(data['humidity'])
        ph = float(data['ph'])
        rainfall = float(data['rainfall'])
        
        # Prepare input data for prediction
        input_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        input_scaled = scaler.transform(input_data)
        
        # Get predictions
        probabilities = model.predict_proba(input_scaled)[0]
        crop_labels = model.classes_
        
        # Get top 3 recommendations
        top_indices = np.argsort(probabilities)[::-1][:3]
        
        recommendations = []
        for i in top_indices:
            crop = crop_labels[i]
            confidence = round(probabilities[i] * 100, 2)
            
            recommendation = {
                'crop': crop.capitalize(),
                'confidence': confidence,
                'fertilizer_recommendations': [],
                'water_management': None
            }
            
            # Add detailed recommendations if available
            if crop in crop_info:
                ideal = crop_info[crop]
                
                # Fertilizer recommendations
                fertilizer_recommendations = []
                
                if N < ideal['N']:
                    deficit = ideal['N'] - N
                    fertilizer_recommendations.append({
                        'type': 'add',
                        'nutrient': 'Nitrogen',
                        'amount': round(deficit, 1),
                        'fertilizer': 'Urea or Ammonium Sulfate'
                    })
                elif N > ideal['N']:
                    excess = N - ideal['N']
                    fertilizer_recommendations.append({
                        'type': 'excess',
                        'nutrient': 'Nitrogen',
                        'amount': round(excess, 1),
                        'note': 'Reduce nitrogen-rich fertilizers'
                    })
                
                if P < ideal['P']:
                    deficit = ideal['P'] - P
                    fertilizer_recommendations.append({
                        'type': 'add',
                        'nutrient': 'Phosphorus',
                        'amount': round(deficit, 1),
                        'fertilizer': 'Single Super Phosphate'
                    })
                elif P > ideal['P']:
                    excess = P - ideal['P']
                    fertilizer_recommendations.append({
                        'type': 'excess',
                        'nutrient': 'Phosphorus',
                        'amount': round(excess, 1),
                        'note': 'Reduce phosphorus fertilizers'
                    })
                
                if K < ideal['K']:
                    deficit = ideal['K'] - K
                    fertilizer_recommendations.append({
                        'type': 'add',
                        'nutrient': 'Potassium',
                        'amount': round(deficit, 1),
                        'fertilizer': 'Muriate of Potash'
                    })
                elif K > ideal['K']:
                    excess = K - ideal['K']
                    fertilizer_recommendations.append({
                        'type': 'excess',
                        'nutrient': 'Potassium',
                        'amount': round(excess, 1),
                        'note': 'Reduce potash application'
                    })
                
                # Check if NPK is perfect
                if (N == ideal['N'] and P == ideal['P'] and K == ideal['K']):
                    fertilizer_recommendations.append({
                        'type': 'perfect',
                        'note': 'Your soil NPK levels are optimal for this crop!'
                    })
                
                recommendation['fertilizer_recommendations'] = fertilizer_recommendations
                
                # Water management
                if 'rainfall' in ideal:
                    if rainfall < ideal['rainfall']:
                        water_deficit = ideal['rainfall'] - rainfall
                        recommendation['water_management'] = {
                            'type': 'deficit',
                            'amount': round(water_deficit, 1),
                            'target': ideal['rainfall'],
                            'note': f'Need additional irrigation'
                        }
                    elif rainfall > ideal['rainfall']:
                        water_excess = rainfall - ideal['rainfall']
                        recommendation['water_management'] = {
                            'type': 'excess',
                            'amount': round(water_excess, 1),
                            'note': 'Ensure good drainage'
                        }
                    else:
                        recommendation['water_management'] = {
                            'type': 'perfect',
                            'target': ideal['rainfall'],
                            'note': 'Rainfall matches ideal requirement'
                        }
                
                # Add ideal values for comparison
                recommendation['ideal_values'] = {
                    'N': ideal['N'],
                    'P': ideal['P'],
                    'K': ideal['K']
                }
                
                # Add current values
                recommendation['current_values'] = {
                    'N': N,
                    'P': P,
                    'K': K
                }
            
            recommendations.append(recommendation)
        
        return jsonify({
            'status': 'success',
            'recommendations': recommendations,
            'input_parameters': {
                'N': N,
                'P': P,
                'K': K,
                'temperature': temperature,
                'humidity': humidity,
                'ph': ph,
                'rainfall': rainfall
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error during prediction: {str(e)}'
        }), 500

@app.route('/api/directory')
def list_directory():
    """API endpoint to list current directory contents for debugging"""
    try:
        current_files = os.listdir(".")
        return jsonify({
            'status': 'success',
            'files': current_files
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Could not list directory contents: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Loading models on startup...")
    status = load_models()
    print(f"Model loading status: {status}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)