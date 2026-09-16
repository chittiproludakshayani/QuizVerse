import asyncio
import csv
import os
from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.utils import secure_filename
from googletrans import Translator
from pymongo import MongoClient
import certifi
import pandas as pd
from joblib import load

# ...existing code...

app = Flask(__name__)
# ...existing code...



# AgroAssist Chatbot route and logic (no blueprint, no circular import)
@app.route('/agroassist', methods=['GET', 'POST'])
def agroassist():
    if 'chatlog' not in session:
        session['chatlog'] = []
    chatlog = session['chatlog']
    if request.method == 'POST':
        user_input = request.form['user_input']
        chatlog.append({'role': 'user', 'text': user_input})
        response = get_agroassist_response(user_input)
        chatlog.append({'role': 'bot', 'text': response})
        session['chatlog'] = chatlog
        return redirect(url_for('agroassist'))
    return render_template('agroassist.html', chatlog=chatlog)

def get_agroassist_response(user_input):
    text = user_input.lower()
    # Crop price Q&A
    if 'price' in text or 'cost' in text:
        prices = get_crop_prices()
        for crop in prices:
            if crop['name'].lower() in text:
                return f"Current price of {crop['name']}: ₹{crop['price']} {crop['unit']} in {crop['market']}."
        return "Please specify the crop name to get the price."
    # Crop recommendation
    if 'recommend' in text or 'which crop' in text:
        return "To get crop recommendations, use the Predict page and enter your soil, weather, and region details."
    # Disease/plant advice
    if 'disease' in text or 'problem' in text or 'plant' in text:
        return "For plant disease diagnosis, use the Crop Doctor page and upload a plant image."
    # Greetings
    if 'hello' in text or 'hi' in text or 'hey' in text:
        return "Hello! I'm AgroAssist, your farming assistant. Ask me about crop prices, advice, or feedback."
    # Fallback
    return "I'm AgroAssist. I can help with crop prices, recommendations, and farming advice. Try asking about a crop price or how to get recommendations."
from textblob import TextBlob
def analyze_sentiment(text):
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        if polarity > 0.2:
            return 'Positive'
        elif polarity < -0.2:
            return 'Negative'
        else:
            return 'Neutral'
    except Exception:
        return 'Unknown'
try:
    client = MongoClient(
        "mongodb+srv://dakshayani:dakshi19@myatlasclusteredu.wizq9sn.mongodb.net/myDB?retryWrites=true&w=majority",
        tls=True,
        tlsCAFile=certifi.where()
    )
    db = client["myDB"]
    collection = db["feedback"]
    mongo_available = True
except Exception:
    client = None
    db = None
    collection = None
    mongo_available = False

app.secret_key = 'replace-this-with-a-secure-key'
DATA_FILE = 'feedback.csv'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
translator = Translator()

UI_TRANSLATIONS = {
    'en': {
        'choose_language': 'Choose Language:',
        'enter_report': 'Enter agriculture report or farmer feedback:',
        'use_voice_input': 'Use Voice Input',
        'get_suggestions': 'Get Suggestions',
        'voice_hint': 'Voice input needs a supported browser and microphone permission. If it fails, type your report in the box.',
        'suggestion_summary': 'Suggestion Summary',
        'recent_feedback_summary': 'Recent Feedback Summary',
        'speak_suggestions': 'Speak Suggestions',
        'home': 'Home',
        'advisor': 'Advisor',
        'crop_prices': 'Crop Prices',
        'current_market': 'Current market prices for major crops (as of April 2026)',
        'crop': 'Crop',
        'price': 'Price',
        'unit': 'Unit',
        'market': 'Market',
        'note_prices': 'Note: Prices are indicative and may vary by location and time. Always check local markets for current rates.',
        'crop_doctor_title': 'Crop Doctor',
        'crop_doctor_subtitle': 'Upload a photo of your plant to diagnose potential issues',
        'select_plant_image': 'Select Plant Image:',
        'analyze_plant': 'Analyze Plant',
        'diagnosis_result': 'Diagnosis Result'
    },
    'te': {
        'choose_language': 'భాషను ఎంచుకోండి:',
        'enter_report': 'వ్యవసాయ నివేదిక లేదా రైతు అభిప్రాయాన్ని నమోదు చేయండి:',
        'use_voice_input': 'వాయిస్ ఇన్‌పుట్ ఉపయోగించండి',
        'get_suggestions': 'సూచనలు పొందండి',
        'voice_hint': 'వాయిస్ ఇన్‌పుట్‌కు మైక్రోఫోనుకు అనుమతి అవసరం. అది విఫలమైతే, బాక్స్లో మీ నివేదికను టైప్ చేయండి.',
        'suggestion_summary': 'సూచనల సారాంశం',
        'recent_feedback_summary': 'ఇటీవలి ప్రతిస్పందన సారాంశం',
        'speak_suggestions': 'సూచనలను చదవండి',
        'home': 'హోమ్',
        'advisor': 'అడ్వజర్',
        'crop_prices': 'క్రాప్ ధరలు',
        'current_market': 'ప్రధాన పంటల కోసం ప్రస్తుత మార్కెట్ ధరలు (ఏప్రిల్ 2026 నాటికి)',
        'crop': 'పంట',
        'price': 'ధర',
        'unit': 'ఒకక పైగా',
        'market': 'మార్కెట్',
        'note_prices': 'గమనిక: ధరలు సూచనాత్మకమైనవి మరియు స్థలం మరియు సందర్భం అనుసరించవచ్చు. ప్రస్తుత రేట్ల కోసం స్థానిక మార్కెట్లను alltid చూడండి.',
        'crop_doctor_title': 'క్రాప్ డాక్టర్',
        'crop_doctor_subtitle': 'మీ మొక్క సమస్యలను తెలుసుకోవడానికి దాని ఫోటోను అప్‌లోడ్ చేయండి',
        'select_plant_image': 'పంట చిత్రం ఎంచుకోండి:',
        'analyze_plant': 'రూపురేఖ విశ్లేషించు',
        'diagnosis_result': 'నిర్ణయ ఫలితం'
    },
    'hi': {
        'choose_language': 'भाषा चुनें:',
        'enter_report': 'कृषि रिपोर्ट या किसान की प्रतिक्रिया दर्ज करें:',
        'use_voice_input': 'वॉइस इनपुट उपयोग करें',
        'get_suggestions': 'सुझाव प्राप्त करें',
        'voice_hint': 'वॉइस इनपुट के लिए समर्थित ब्राउज़र और माइक्रोफोन अनुमति आवश्यक है। यदि यह विफल हो जाए, तो बॉक्स में अपनी रिपोर्ट टाइप करें।',
        'suggestion_summary': 'सुझाव सारांश',
        'recent_feedback_summary': 'हाल की प्रतिक्रिया सारांश',
        'speak_suggestions': 'सुझाव बोलें',
        'home': 'होम',
        'advisor': 'सलाहकार',
        'crop_prices': 'फसल मूल्य',
        'current_market': 'मुख्य फसलों के लिए वर्तमान बाजार मूल्य (अप्रैल 2026 तक)',
        'crop': 'फसल',
        'price': 'मूल्य',
        'unit': 'प्रति किग्रा',
        'market': 'बाजार',
        'note_prices': 'नोट: कीमतें संकेतात्मक हैं और स्थान और समय के अनुसार भिन्न हो सकती हैं। वर्तमान दरों के लिए हमेशा स्थानीय बाजार देखें।',
        'crop_doctor_title': 'फसल डॉक्टर',
        'crop_doctor_subtitle': 'अपनी पौधे की समस्या का पता लगाने के लिए उसकी तस्वीर अपलोड करें',
        'select_plant_image': 'पौधे की छवि चुनें:',
        'analyze_plant': 'पौधे का विश्लेषण करें',
        'diagnosis_result': 'निदान परिणाम'
    },
    'ta': {
        'choose_language': 'மொழியை தேர்ந்தெடுங்கள்:',
        'enter_report': 'கிராமிய அறிக்கை அல்லது விவசாயி கருத்து உள்ளிடவும்:',
        'use_voice_input': 'ஒலி உள்ளீட்டை பயன்படுத்தவும்',
        'get_suggestions': 'பரிந்துரைகளைப் பெறவும்',
        'voice_hint': 'ஒலி உள்ளீட்டிற்கு ஆதரிக்கப்படும் உலாவி மற்றும் மைக்ரோபோன் அனுமதி தேவை. அது தோல்வியடைந்தால், உங்கள் அறிக்கையை பெட்டியில் টাইப் செய்யவும்.',
        'suggestion_summary': 'பரிந்துரைகள் சுருக்கம்',
        'recent_feedback_summary': 'சமீபத்திய கருத்து சுருக்கம்',
        'speak_suggestions': 'பரிந்துரைகளை பேசவும்',
        'home': 'முகப்பு',
        'advisor': 'ஆலோசகர்',
        'crop_prices': 'பயிர் விலைகள்',
        'current_market': 'முக்கிய பயிர்களுக்கு தற்போதைய சந்தை விலைகள் (ஏப்ரல் 2026 வரை)',
        'crop': 'பயிர்',
        'price': 'விலை',
        'unit': 'ஒரு கிலோக்கு',
        'market': 'சந்தை',
        'note_prices': 'குறிப்பு: விலைகள் குறிப்பு மட்டுமே மற்றும் இடம் மற்றும் நேரப்படி மாறலாம். தற்போதைய விகிதங்களுக்கு எப்போதும் உள்ளூர் சந்தைகளைப் பார்க்கவும்.',
        'crop_doctor_title': 'பயிர் டாக்டர்',
        'crop_doctor_subtitle': 'உங்கள் தாவரத்தின் பிரச்சனையை கண்டறிய அதன் புகைப்படத்தை பதிவேற்றவும்',
        'select_plant_image': 'தாவரப் படம் தேர்வு செய்யவும்:',
        'analyze_plant': 'தாவரத்தை பகுப்பாய்வு செய்க',
        'diagnosis_result': 'நிர்ணய முடிவு'
    },
    'kn': {
        'choose_language': 'ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ:',
        'enter_report': 'ಕೃಷಿ ವರದಿ ಅಥವಾ ರೈತ ಪ್ರತಿಕ್ರಿಯೆಯನ್ನು ನಮೂದಿಸಿ:',
        'use_voice_input': 'ವಾಯ್ಸ್ ಇನ್ಪುಟ್ ಬಳಸಿ',
        'get_suggestions': 'ಸಲಹೆಗಳು ಪಡೆಯಿರಿ',
        'voice_hint': 'ವಾಯ್ಸ್ ಇನ್ಪುಟ್‌ಗೆ ಬೆಂಬಲBrowser ಮತ್ತು ಮೈಕ್ರೊಫೋನ್ ಅನುಮತಿಯ ಅಗತ್ಯವಿದೆ. ಇದು ವಿಫಲವಾದರೆ, ಬಾಕ್ಸ್‌ನಲ್ಲಿ ನಿಮ್ಮ ವರದಿಯನ್ನು ಟೈಪ್ ಮಾಡಿ.',
        'suggestion_summary': 'ಸಲಹೆಗಳ ಸಾರಾಂಶ',
        'recent_feedback_summary': 'ಇತ್ತೀಚಿನ ಪ್ರತಿಕ್ರಿಯೆ ಸಾರಾಂಶ',
        'speak_suggestions': 'ಸಲಹೆಗಳನ್ನು ಮಾತನಾಡಿ',
        'home': 'ಮುಖಪುಟ',
        'advisor': 'ಸಲಹೆಗಾರ',
        'crop_prices': 'ಹಣಿಕೈನ ಬೆಲೆಗಳು',
        'current_market': 'ಪ್ರಮುಖ ಫসল್ಗಳಿಗಾಗಿ ಪ್ರಸ್ತುತ ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು (ಏಪ್ರಿಲ್ 2026 ರ ವರೆಗೆ)',
        'crop': 'ಫಸಲು',
        'price': 'ಬೆಲೆ',
        'unit': 'ಪ್ರತಿ ಕೆಜಿ',
        'market': 'ಮಾರುಕಟ್ಟೆ',
        'note_prices': 'ಗಮನಿಸಿ: ಬೆಲೆಗಳು ಸೂಚನಾತ್ಮಕವಾಗಿವೆ ಮತ್ತು ಸ್ಥಳ ಮತ್ತು ಕಾಲಮ್ ಪ್ರಕಾರ ಬದಲಾಗಬಹುದು. ಪ್ರಸ್ತುತ ದರಗಳಿಗಾಗಿ ಸ್ಥಳೀಯ ಮಾರುಕಟ್ಟೆಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.',
        'crop_doctor_title': 'ಫಸಲು ಡಾಕ್ಟರ್',
        'crop_doctor_subtitle': 'ನಿಮ್ಮ ಬೆಳೆ ಸಮಸ್ಯೆಯನ್ನು ಗೊತ್ತಾಗಿಸಲು ಅದರ ಚಿತ್ರವನ್ನು ಅಪ್ಲೋಡ್ ಮಾಡಿ',
        'select_plant_image': 'ಬೆಳೆ ಚಿತ್ರವನ್ನು ಆಯ್ಕೆಮಾಡಿ:',
        'analyze_plant': 'ಬೆಳೆಯನ್ನು ವಿಶ್ಲೇಷಿಸಿ',
        'diagnosis_result': 'ನಿರ್ಣಯ ಫಲಿತಾಂಶ'
    },
    'ml': {
        'choose_language': 'ഭാഷ തിരഞ്ഞെടുത്ത്:',
        'enter_report': 'കൃഷി റിപ്പോർട്ട് അല്ലെങ്കിൽ കര്‍ഷകന്റെ പ്രതികരണം നൽകുക:',
        'use_voice_input': 'വോയ‌സ് ഇൻപുട്ട് ഉപയോഗിക്കുക',
        'get_suggestions': 'സൂചനകൾ നേടുക',
        'voice_hint': 'വോയ്സ് ഇൻപുട്ടിനു പിന്തുണയുള്ള ബ്രൗസറും മൈക്രോഫോൺ അനുവാദവും ആവശ്യമാണ്. അത് പരാജയമാകുകയാണെങ്കിൽ, ബോക്സിൽ നിങ്ങളുടെ റിപ്പോർട്ട് ടൈപ്പ് ചെയ്യുക.',
        'suggestion_summary': 'സൂചന സാരാംശം',
        'recent_feedback_summary': 'സമീപകാല പ്രതികരണം സാരാംശം',
        'speak_suggestions': 'സൂചനകൾ പറയൂ',
        'home': 'ഹോം',
        'advisor': 'അഡ്വൈസർ',
        'crop_prices': 'നിരക്കുകൾ',
        'current_market': 'പ്രധാന വിളകൾക്കുള്ള നിലവിലെ വിപണി നിരക്കുകൾ (ഏപ്രിൽ 2026 വരെ)',
        'crop': 'വളം',
        'price': 'വില',
        'unit': 'ഒരു കിലോയ്ക്ക്',
        'market': 'മാർക്കറ്റ്',
        'note_prices': 'കുറിപ്പ്: വിലകൾ സൂചനകൾ മാത്രമാണ്; സ്ഥലം மற்றும் സമയം അനുസരിച്ച് വ്യത്യാസപ്പെടാം. നിലവിലെ നിരക്കുകൾക്കായി എല്ലാ പ്രാദേശിക മാർക്കറ്റുകളും പരിശോധിക്കുക.',
        'crop_doctor_title': 'ക്രോപ് ഡോക്ടർ',
        'crop_doctor_subtitle': 'താങ്കളുടെ ചെടിയുടെ പ്രശ്നം കണ്ടെത്താൻ അതിന്റെ ചിത്രം അപ്ലോഡ് ചെയ്യുക',
        'select_plant_image': 'സസ്യ ചിത്രം തിരഞ്ഞെടുക്കുക:',
        'analyze_plant': 'ചെടി വിശകലനം ചെയ്യുക',
        'diagnosis_result': 'നിര്ണയ ഫലം'
    },
    'bn': {
        'choose_language': 'ভাষা নির্বাচন করুন:',
        'enter_report': 'কৃষি প্রতিবেদন বা কৃষকের প্রতিক্রিয়া লিখুন:',
        'use_voice_input': 'ভয়েস ইনপুট ব্যবহার করুন',
        'get_suggestions': 'পরামর্শ পান',
        'voice_hint': 'ভয়েস ইনপুটের জন্য সমর্থিত ব্রাউজার এবং মাইক্রোফোন অনুমতি প্রয়োজন। যদি এটি ব্যর্থ হয়, তাহলে বাক্সে আপনার প্রতিবেদন টাইপ করুন।',
        'suggestion_summary': 'পরামর্শ সারাংশ',
        'recent_feedback_summary': 'সাম্প্রতিক প্রতিক্রিয়া সারাংশ',
        'speak_suggestions': 'পরামর্শ পড়ুন',
        'home': 'হোম',
        'advisor': 'উপদেষ্টা',
        'crop_prices': 'ফসলের মূল্য',
        'current_market': 'প্রধান ফসলের জন্য বর্তমান বাজার মূল্য (এপ্রিল 2026 পর্যন্ত)',
        'crop': 'ফসল',
        'price': 'দাম',
        'unit': 'প্রতি কেজি',
        'market': 'বাজার',
        'note_prices': 'নোট: দাম নির্দেশিক এবং স্থান ও সময় অনুযায়ী পরিবর্তিত হতে পারে। বর্তমান রেটের জন্য সর্বদা স্থানীয় বাজার পরীক্ষা করুন।',
        'crop_doctor_title': 'ক্রপ ডাক্তার',
        'crop_doctor_subtitle': 'আপনার গাছের সমস্যাটি নির্ণয় করতে এর ছবি আপলোড করুন',
        'select_plant_image': 'অপেক্ষিত গাছের ছবি নির্বাচন করুন:',
        'analyze_plant': 'গাছ বিশ্লেষণ করুন',
        'diagnosis_result': 'নিদান ফলাফল'
    }
}

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        new_loop = asyncio.new_event_loop()
        try:
            return new_loop.run_until_complete(coro)
        finally:
            new_loop.close()
    return asyncio.run(coro)

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    message = request.form.get("message")

    insert_feedback_document({
        "name": name,
        "message": message
    })

    return "Saved successfully ✅"

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    best_crop = None
    harvest_advice = None
    matched_crops = []
    if request.method == 'POST':
        soil = request.form['soil']
        weather = request.form['weather']
        region = request.form.get('region', 'unknown')

        # Load model and encoders
        clf = load('crop_model.joblib')
        le_soil = load('le_soil.joblib')
        le_weather = load('le_weather.joblib')
        le_region = load('le_region.joblib')
        le_crop = load('le_crop.joblib')

        # Encode input
        try:
            soil_enc = le_soil.transform([soil])[0]
        except Exception:
            soil_enc = 0
        try:
            weather_enc = le_weather.transform([weather])[0]
        except Exception:
            weather_enc = 0
        try:
            region_enc = le_region.transform([region])[0]
        except Exception:
            region_enc = 0

        X_input = [[soil_enc, weather_enc, region_enc]]
        pred_enc = clf.predict(X_input)[0]
        best_crop = le_crop.inverse_transform([pred_enc])[0]

        # Advice dictionary (same as before)
        advice = {
            'Wheat': 'Harvest when grain moisture is 14-20%. Use a combine harvester or cut and thresh manually for small plots.',
            'Rice': 'Harvest when the grains are golden and firm. Bundle stalks and thresh soon after cutting to prevent grain shattering.',
            'Corn': 'Harvest when kernels are full and firm. Use a harvester for large fields or pick ears by hand for smaller plots.',
            'Soybeans': 'Harvest once pods are dry and leaves have yellowed. Use a combine or pull up plants and thresh if weather is wet.',
            'Barley': 'Harvest when kernels are hard and dry. Swath or straight combine depending on field conditions.',
            'Millet': 'Harvest when the panicles are golden and grains are hard. Cut and thresh when dry.',
            'Potato': 'Harvest when foliage yellows. Lift tubers carefully to avoid damage and store in cool, dry conditions.',
            'Cotton': 'Harvest when bolls are open and dry. Use a cotton picker for large fields or hand-pick for small plots.',
            'Sugarcane': 'Harvest when stalks are mature and sweet. Cut close to the ground and remove leaves before crushing.',
            'Tea': 'Harvest the top two leaves and bud. Pluck carefully in the morning for best quality.',
            'Groundnut': 'Harvest when lower leaves turn yellow and pods are mature. Uproot plants and dry pods in the sun.'
        }
        harvest_advice = advice.get(best_crop, 'Use standard harvest practices for this crop.')
        matched_crops = [{'name': best_crop, 'score': 1, 'demand': '', 'production': '', 'advice': harvest_advice}]

    return render_template('predict.html', best_crop=best_crop, harvest_advice=harvest_advice, matched_crops=matched_crops)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    message = None
    selected_language = request.form.get('language', 'en') if request.method == 'POST' else 'en'
    # Handle delete request
    if request.method == 'POST' and 'delete_feedback' in request.form:
        delete_index = int(request.form['delete_feedback'])
        feedbacks = load_feedback()
        if 0 <= delete_index < len(feedbacks):
            del feedbacks[delete_index]
            # Rewrite the CSV file
            with open(DATA_FILE, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['name', 'region', 'crop', 'soil', 'weather', 'notes']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for fb in feedbacks:
                    writer.writerow(fb)
            message = 'Feedback deleted.'
    elif request.method == 'POST':
        form_data = {
            'name': request.form['name'],
            'region': request.form['region'],
            'crop': request.form['crop'],
            'soil': request.form['soil'],
            'weather': request.form['weather'],
            'notes': request.form['notes']
        }
        insert_feedback_document(form_data)
        message = 'Feedback submitted successfully.'
    # Load all feedbacks for display
    all_feedbacks = load_feedback()
    return render_template('feedback.html', message=message, selected_language=selected_language, all_feedbacks=all_feedbacks)

@app.route('/advisor', methods=['GET', 'POST'])
def advisor():
    suggestions = None
    previous_feedback = []
    selected_language = 'en'
    ui = UI_TRANSLATIONS[selected_language]
    if request.method == 'POST':
        report = request.form['report']
        selected_language = request.form.get('language', 'en')
        ui = UI_TRANSLATIONS.get(selected_language, UI_TRANSLATIONS['en'])
        detected_lang = detect_language(report)
        if not detected_lang:
            # Fallback detection based on unicode ranges
            if any(0x0C00 <= ord(c) <= 0x0C7F for c in report):  # Telugu
                detected_lang = 'te'
            elif any(0x0900 <= ord(c) <= 0x097F for c in report):  # Hindi/Devanagari
                detected_lang = 'hi'
            elif any(0x0B80 <= ord(c) <= 0x0BFF for c in report):  # Tamil
                detected_lang = 'ta'
            elif any(0x0C80 <= ord(c) <= 0x0CFF for c in report):  # Kannada
                detected_lang = 'kn'
            elif any(0x0D00 <= ord(c) <= 0x0D7F for c in report):  # Malayalam
                detected_lang = 'ml'
            elif any(0x0980 <= ord(c) <= 0x09FF for c in report):  # Bengali
                detected_lang = 'bn'
        if detected_lang and detected_lang in ['en', 'hi', 'te', 'ta', 'kn', 'ml', 'bn']:
            response_language = detected_lang
        else:
            response_language = selected_language
        suggestions = analyze_report(report, response_language)
        previous_feedback = summarize_feedback(response_language)
    return render_template('advisor.html', ui=ui, suggestions=suggestions, previous_feedback=previous_feedback, selected_language=selected_language)

@app.route('/nlp', methods=['GET', 'POST'])
def nlp():
    insight = None
    if request.method == 'POST':
        text = request.form['text']
        # Mock NLP: word count
        word_count = len(text.split())
        insight = f"The text contains {word_count} words."
    return render_template('nlp.html', insight=insight)

@app.route('/crop-doctor', methods=['GET', 'POST'])
def crop_doctor():
    diagnosis = None
    selected_language = 'en'
    ui = UI_TRANSLATIONS[selected_language]
    if request.method == 'POST':
        file = request.files.get('plant_image')
        selected_language = request.form.get('language', 'en')
        ui = UI_TRANSLATIONS.get(selected_language, UI_TRANSLATIONS['en'])
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            diagnosis = analyze_plant_image(filepath, selected_language)
            os.remove(filepath)
        # If diagnosis is present but not translated (e.g., from previous session), translate it
        if diagnosis and selected_language != 'en':
            diagnosis = translate_text(diagnosis, selected_language)
    return render_template('crop_doctor.html', diagnosis=diagnosis, selected_language=selected_language, ui=ui)


@app.route('/crop-prices')
def crop_prices():
    selected_language = request.args.get('language', 'en')
    ui = UI_TRANSLATIONS.get(selected_language, UI_TRANSLATIONS['en'])
    prices = get_crop_prices()
    translated_prices = []
    for crop in prices:
        translated_crop = {
            'name': translate_text(crop['name'], selected_language),
            'price': crop['price'],
            'unit': translate_text(crop['unit'], selected_language),
            'market': translate_text(crop['market'], selected_language)
        }
        translated_prices.append(translated_crop)
    return render_template('crop_prices.html', prices=translated_prices, selected_language=selected_language, ui=ui)

# Route to edit crop prices
@app.route('/edit-crop-prices', methods=['GET', 'POST'])
def edit_crop_prices():
    csv_path = os.path.join(os.path.dirname(__file__), 'crop_prices.csv')
    if request.method == 'POST':
        count = int(request.form.get('count', 0))
        new_prices = []
        for i in range(count):
            name = request.form.get(f'name_{i}', '').strip()
            price = request.form.get(f'price_{i}', '').strip()
            unit = request.form.get(f'unit_{i}', '').strip()
            market = request.form.get(f'market_{i}', '').strip()
            if name and price and unit and market:
                new_prices.append({'name': name, 'price': price, 'unit': unit, 'market': market})
        # Write to CSV (overwrite)
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            csvfile.write('# This CSV file will store the latest crop prices for the app.\n')
            csvfile.write('# Columns: name,price,unit,market\n')
            writer = csv.DictWriter(csvfile, fieldnames=['name', 'price', 'unit', 'market'])
            for row in new_prices:
                writer.writerow(row)
        return render_template('edit_crop_prices.html', prices=new_prices, message='Prices updated successfully!')
    # GET: load current prices
    prices = get_crop_prices()
    return render_template('edit_crop_prices.html', prices=prices)

def save_feedback(data):
    exists = os.path.isfile(DATA_FILE)
    data.pop("_id", None)
    with open(DATA_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'region', 'crop', 'soil', 'weather', 'notes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow(data)


def load_feedback():
    if not os.path.isfile(DATA_FILE):
        return []
    with open(DATA_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        feedbacks = list(reader)
        # Add sentiment to each feedback
        for fb in feedbacks:
            fb['sentiment'] = analyze_sentiment(fb.get('notes', ''))
        return feedbacks


# Download feedback as CSV
from flask import send_file
from sklearn.linear_model import LinearRegression
import numpy as np
@app.route('/download/feedback')
def download_feedback():
    if not os.path.isfile(DATA_FILE):
        return 'No feedback data available.'
    return send_file(DATA_FILE, as_attachment=True)

# Download predictions as CSV (mock: use feedback.csv for now)
@app.route('/download/predictions')
def download_predictions():
    # If you have a separate predictions file, use it here
    if not os.path.isfile(DATA_FILE):
        return 'No prediction data available.'
    return send_file(DATA_FILE, as_attachment=True)


def summarize_feedback(language='en'):
    feedback = load_feedback()
    if not feedback:
        return [translate_text('No previous feedback available yet.', language)]

    issues = {
        'dry': 0,
        'pest': 0,
        'disease': 0,
        'yield': 0,
        'soil': 0,
        'weather': 0
    }
    for item in feedback:
        notes = item['notes'].lower()
        for key in issues:
            if key in notes:
                issues[key] += 1

    summary = []
    for key, count in issues.items():
        if count > 0:
            summary.append(translate_text(f"{count} reports mention {key}.", language))
    if not summary:
        summary.append(translate_text('Previous reports do not contain common issue keywords.', language))
    return summary


def analyze_report(text, language='en'):
    original_lower = text.lower()
    translated_lower = original_lower

    detected_lang = detect_language(text)
    if detected_lang and detected_lang != 'en':
        try:
            text_english = run_async(translator.translate(text, src=detected_lang, dest='en')).text
            translated_lower = text_english.lower()
        except Exception:
            translated_lower = original_lower

    suggestions = []
    matched = False

    def any_keyword(keywords):
        return any(keyword in translated_lower for keyword in keywords) or any(keyword in original_lower for keyword in keywords)

    if any_keyword(['harvest', 'cutting', 'pick', 'reap', 'gathering', 'when to cut', 'when to harvest', 'విత్తనం', 'కోత']):
        matched = True
        if any_keyword(['tomato', 'టమాటా']):
            suggestions.append('Harvest tomatoes when they are fully colored and firm. Pick regularly to encourage more production. Store at room temperature away from direct sunlight.')
        elif any_keyword(['rice', 'paddy', 'బియ్యం', 'నేతి']):
            suggestions.append('Harvest rice when grains are golden and firm and the panicle is mature. Thresh soon after cutting to avoid losses.')
        elif any_keyword(['wheat', 'గోధుమ']):
            suggestions.append('Harvest wheat when the grains are golden and firm. Cut near the base and thresh when crop moisture is around 14-20%.')
        elif any_keyword(['cotton', 'పత్తి']):
            suggestions.append('Harvest cotton when bolls are open and dry. Pick mature bolls only and avoid wet conditions to reduce staining.')
        elif any_keyword(['potato', 'ఉరుక్కాయ']):
            suggestions.append('Harvest potatoes when foliage yellows and withers. Lift tubers carefully, dry them well, and store in cool, ventilated conditions.')
        elif any_keyword(['corn', 'maize', 'జొన్న']):
            suggestions.append('Harvest corn when kernels are hard and dry. For sweet corn, pick when the silks turn brown and the ear is tender.')
        else:
            suggestions.append('Harvest when the crop is mature, grains or fruits are firm, and weather is suitable. Use sharp tools and avoid damaging produce.')

    if any_keyword(['storage', 'store', 'preserve', 'keep', 'how long', 'నిల్వ']):
        matched = True
        if any_keyword(['tomato', 'టమాటా']):
            suggestions.append('Store ripe tomatoes at room temperature for up to a week. Refrigerate only if overripe. Do not store with ethylene-producing fruits like apples.')
        elif any_keyword(['rice', 'paddy', 'బియ్యం', 'నేతి']):
            suggestions.append('Store rice grains in airtight containers in a cool, dry place. Maintain moisture below 14% and protect from insects and rodents.')
        elif any_keyword(['wheat', 'గోధుమ']):
            suggestions.append('Store wheat in clean, dry bins. Keep moisture below 14% and temperature below 25°C. Use fumigation if needed for pest control.')
        elif any_keyword(['cotton', 'పత్తి']):
            suggestions.append('Store cotton in bales in dry warehouses. Protect from moisture, insects, and fire. Maintain humidity below 60%.')
        elif any_keyword(['potato', 'ఉరుక్కాయ']):
            suggestions.append('Store potatoes in dark, cool (7-10°C), ventilated conditions. Avoid light to prevent greening and sprouting.')
        elif any_keyword(['corn', 'maize', 'జొన్న']):
            suggestions.append('Store corn at 13-15% moisture in dry, well-ventilated bins. Use aeration to maintain quality and prevent mold.')
        else:
            suggestions.append('Store produce in a dry, cool, and well-ventilated place. Use clean containers or bags, protect from pests, and keep moisture low.')

    if any_keyword(['plant', 'sow', 'seed', 'when to plant', 'timing', 'transplant', 'విత్తనం', 'నాటండి', 'పుల్లేరు']):
        matched = True
        if any_keyword(['wheat', 'గోధుమ']):
            suggestions.append('Sow wheat in October-November in most regions. Use good quality seeds and prepare well-drained, fertile soil.')
        elif any_keyword(['rice', 'paddy', 'బియ్యం', 'నేతి']):
            suggestions.append('Plant rice in the monsoon season. Prepare puddled fields for transplanting and maintain shallow water during early growth.')
        elif any_keyword(['cotton', 'పత్తి']):
            suggestions.append('Plant cotton in March-April. Use treated seeds, maintain 15-20 cm spacing, and ensure soil temperature is adequate.')
        elif any_keyword(['tomato', 'టమాటా']):
            suggestions.append('Plant tomatoes in February-March or September-October. Use healthy seedlings, space 45-60 cm apart in rows 60-75 cm apart. Provide support with stakes or cages. Ensure well-drained soil with pH 6-7 and full sunlight.')
        else:
            suggestions.append('Plant at the right local season, use good quality seeds, and prepare soil with organic matter and proper drainage.')

    if any_keyword(['disease', 'blight', 'mildew', 'rot', 'rust', 'wilt', 'sick', 'infection', 'yellow leaves', 'spots', 'lesions', 'leaf spot']):
        matched = True
        if any_keyword(['tomato', 'టమాటా']):
            suggestions.append('Watch for early blight, late blight, and fusarium wilt. Use disease-resistant varieties, avoid overhead watering, and apply copper fungicide preventively. Remove affected leaves immediately.')
        elif any_keyword(['rice', 'paddy', 'బియ్యం', 'నేతి']):
            suggestions.append('Watch for rice blast, bacterial blight, and sheath blight. Use resistant varieties, avoid excessive nitrogen, and apply fungicides like tricyclazole. Ensure proper field drainage.')
        elif any_keyword(['wheat', 'గోధుమ']):
            suggestions.append('Watch for rust, powdery mildew, and loose smut. Use resistant varieties, apply fungicides like propiconazole, and rotate crops to prevent disease buildup.')
        elif any_keyword(['cotton', 'పత్తి']):
            suggestions.append('Watch for wilt, root rot, and bacterial blight. Use resistant varieties, improve soil drainage, and apply copper-based fungicides.')
        elif any_keyword(['potato', 'ఉరుక్కాయ']):
            suggestions.append('Watch for late blight and early blight. Use certified seeds, avoid wet conditions, and apply fungicides like mancozeb preventively.')
        elif any_keyword(['corn', 'maize', 'జొన్న']):
            suggestions.append('Watch for corn smut, gray leaf spot, and northern corn leaf blight. Use resistant hybrids, crop rotation, and fungicides if needed.')
        else:
            suggestions.append('Inspect affected plants, remove and destroy diseased material, and follow crop-specific disease control measures. Improve air circulation and avoid overhead irrigation.')
            suggestions.append('Use disease-resistant varieties, rotate crops, and apply recommended fungicides only when necessary.')

    if any_keyword(['pest', 'insect', 'worm', 'bug', 'caterpillar', 'aphid', 'beetle', 'locust', 'grasshopper', 'borer']):
        matched = True
        if any_keyword(['tomato', 'టమాటా']):
            suggestions.append('Common tomato pests include aphids, tomato hornworms, and fruit borers. Use neem oil spray, introduce ladybugs, and hand-pick large pests. Avoid broad-spectrum insecticides near harvest.')
        elif any_keyword(['rice', 'paddy', 'బియ్యం', 'నేతి']):
            suggestions.append('Common rice pests include stem borers, leaf folders, and brown plant hoppers. Use light traps, neem oil, and release trichogramma wasps. Avoid overuse of insecticides.')
        elif any_keyword(['wheat', 'గోధుమ']):
            suggestions.append('Common wheat pests include aphids, armyworms, and Hessian flies. Use seed treatment, crop rotation, and biological control with parasitic wasps.')
        elif any_keyword(['cotton', 'పత్తి']):
            suggestions.append('Common cotton pests include bollworms, aphids, and whiteflies. Use pheromone traps, neem oil, and introduce natural enemies like ladybugs.')
        elif any_keyword(['potato', 'ఉరుక్కాయ']):
            suggestions.append('Common potato pests include Colorado potato beetles, aphids, and potato tuber moths. Use crop rotation, neem oil, and row covers.')
        elif any_keyword(['corn', 'maize', 'జొన్న']):
            suggestions.append('Common corn pests include corn borers, aphids, and corn earworms. Use crop rotation, neem oil, and beneficial insects like lacewings.')
        else:
            suggestions.append('Use Integrated Pest Management: monitor regularly, encourage natural enemies, and use traps or physical removal when possible.')
            suggestions.append('Apply organic controls like neem oil or soap spray before turning to chemical pesticides. Always follow label instructions.')

    if any_keyword(['water', 'dry', 'irrigation', 'rain', 'flood', 'waterlogged', 'drought', 'moisture']):
        matched = True
        if any_keyword(['tomato', 'టమాటా']):
            suggestions.append('Water tomatoes regularly to keep soil moist but not waterlogged. Irrigate at the base to avoid wetting leaves. Use drip irrigation if possible. Water deeply 2-3 times per week, more during fruiting stage.')
        elif any_keyword(['rice', 'paddy', 'బియ్యం', 'నేతి']):
            suggestions.append('Rice requires flooded conditions during growth. Maintain 5-10 cm water depth, reduce before harvest. Use alternate wetting and drying for water efficiency.')
        elif any_keyword(['wheat', 'గోధుమ']):
            suggestions.append('Wheat needs moderate watering. Irrigate at critical stages: crown root initiation, jointing, and grain filling. Avoid water stress during flowering.')
        elif any_keyword(['cotton', 'పత్తి']):
            suggestions.append('Cotton requires regular irrigation. Water every 7-10 days, more frequently during boll formation. Use furrow irrigation to conserve water.')
        elif any_keyword(['potato', 'ఉరుక్కాయ']):
            suggestions.append('Potatoes need even moisture. Water regularly to prevent cracking, especially during tuber formation. Avoid overhead watering to prevent blight.')
        elif any_keyword(['corn', 'maize', 'జొన్న']):
            suggestions.append('Corn needs deep watering. Irrigate every 5-7 days, ensuring 2-3 inches per week. Water deeply to encourage root growth.')
        elif any_keyword(['dry', 'drought', 'no rain', 'water shortage']):
            suggestions.append('Increase irrigation frequency, mulch the soil, and monitor moisture daily. Water in the early morning or late evening to reduce evaporation.')
        elif any_keyword(['flood', 'waterlogged', 'standing water']):
            suggestions.append('Improve drainage, avoid overwatering, and raise the crop beds if possible. Keep the field aerated to prevent root rot.')
        else:
            suggestions.append('Follow a regular irrigation schedule based on crop stage, soil type, and weather conditions. Use drip irrigation if available.')

    if any_keyword(['fertilizer', 'nutrient', 'yellow', 'deficiency', 'nitrogen', 'phosphorus', 'potassium', 'leaf yellowing', 'stunted']):
        matched = True
        if any_keyword(['tomato', 'టమాటా']):
            suggestions.append('Apply balanced NPK fertilizer (10-10-10) at planting, then side-dress with nitrogen during growth. Add calcium for blossom end rot prevention. Use compost or well-rotted manure for organic nutrition.')
        elif any_keyword(['rice', 'paddy', 'బియ్యం', 'నేతి']):
            suggestions.append('Rice needs nitrogen-rich fertilizers. Apply urea in split doses: basal, tillering, and panicle initiation. Use phosphorus and potassium for root development and grain filling.')
        elif any_keyword(['wheat', 'గోధుమ']):
            suggestions.append('Wheat requires nitrogen, phosphorus, and potassium. Apply NPK (20-20-0) at sowing, followed by nitrogen top-dressing at tillering and jointing stages.')
        elif any_keyword(['cotton', 'పత్తి']):
            suggestions.append('Cotton needs balanced fertilization. Apply NPK (20-10-10) at planting, with additional nitrogen during vegetative growth. Zinc and boron are often deficient.')
        elif any_keyword(['potato', 'ఉరుక్కాయ']):
            suggestions.append('Potatoes benefit from high potassium. Apply NPK (15-15-30) at planting, with additional nitrogen during tuber initiation. Avoid excess nitrogen to prevent excessive foliage.')
        elif any_keyword(['corn', 'maize', 'జొన్న']):
            suggestions.append('Corn requires nitrogen and phosphorus. Apply NPK (30-15-0) at planting, with side-dressing of nitrogen at knee-high stage. Potassium helps with drought tolerance.')
        else:
            suggestions.append('Do a soil test to identify nutrient deficiencies. Apply balanced fertilizers and micronutrients according to the test results.')
            suggestions.append('Use organic matter such as compost or manure to improve soil health and nutrient availability.')

    if any_keyword(['soil', 'red soil', 'clay', 'loamy', 'sandy', 'black soil', 'chalky', 'pH']):
        matched = True
        if any_keyword(['red soil', 'ఎర్ర నేల']):
            suggestions.append('Red soil is acidic and low in nutrients. Add lime and organic matter, and grow pulses, groundnuts, or cotton.')
        elif any_keyword(['clay', 'చెక్కగని']):
            suggestions.append('Clay soil holds water but drains slowly. Add compost and sand to improve structure and avoid waterlogging.')
        elif any_keyword(['sandy', 'నుడు']):
            suggestions.append('Sandy soil drains quickly and needs frequent watering. Add organic matter and mulch to retain moisture.')
        elif any_keyword(['black soil', 'కత్తి నేల']):
            suggestions.append('Black soil retains moisture well and is good for cotton and sugarcane. Maintain drainage during heavy rains.')
        else:
            suggestions.append('Test your soil for pH and nutrients, and add organic matter regularly to improve fertility.')

    if any_keyword(['temperature', 'hot', 'cold', 'cool', 'frost', 'heat', 'weather', 'climate']):
        matched = True
        if any_keyword(['hot', 'heat']):
            suggestions.append('Use shade, mulch, and timely irrigation to protect crops during heat. Choose heat-tolerant varieties when available.')
        elif any_keyword(['cold', 'frost']):
            suggestions.append('Protect plants from cold with covers or mulches, and avoid late planting in frost-prone areas.')
        else:
            suggestions.append('Keep an eye on local weather forecasts and adjust farming operations accordingly.')

    if any_keyword(['tomato', 'టమాటా', 'rice', 'paddy', 'బియ్యం', 'నేతి', 'wheat', 'గోధుమ', 'cotton', 'పత్తి', 'potato', 'ఉరుక్కాయ', 'corn', 'maize', 'జొన్న']):
        matched = True
        if any_keyword(['tomato', 'టమాటా']):
            suggestions.append('Tomato cultivation guide: Plant in February-March or September-October in well-drained soil with pH 6-7. Space 45-60 cm apart and support with stakes or cages. Water regularly at the base. Harvest when fruits are fully colored and firm, and store at room temperature away from direct sunlight.')
            suggestions.append('Fertilizer Advice: Apply 10-10-10 NPK at 1000 kg/ha as basal, then side-dress with 50 kg/ha nitrogen at flowering. Use compost or well-rotted manure for organic nutrition.')
            suggestions.append('Pesticide Advice: Use neem oil spray for aphids and hornworms. For blight, apply copper oxychloride (2.5g/liter) preventively. Remove affected leaves immediately.')
        elif any_keyword(['rice', 'paddy', 'బియ్యం', 'నేతి']):
            suggestions.append('Rice cultivation guide: Plant in the monsoon season in puddled, well-drained fields with fertile soil. Maintain shallow water during early growth. Harvest when grains are golden and firm, then thresh soon to avoid losses.')
            suggestions.append('Fertilizer Advice: Apply urea (N) at 100 kg/ha in 3 splits (basal, tillering, panicle initiation), phosphorus (P2O5) 60 kg/ha, potassium (K2O) 40 kg/ha.')
            suggestions.append('Pesticide Advice: For stem borers, use triazophos (2 ml/liter); for blast, apply tricyclazole (0.6g/liter). Use light traps for hoppers.')
        elif any_keyword(['wheat', 'గోధుమ']):
            suggestions.append('Wheat cultivation guide: Sow in October-November in loamy or alluvial soil. Harvest when grains are golden and dry, and store in cool, dry bins.')
            suggestions.append('Fertilizer Advice: Apply NPK (20-20-0) at 120 kg/ha at sowing, then top-dress with 60 kg/ha nitrogen at tillering and jointing.')
            suggestions.append('Pesticide Advice: For rust, use propiconazole (1 ml/liter); for aphids, use imidacloprid (0.3 ml/liter).')
        elif any_keyword(['cotton', 'పత్తి']):
            suggestions.append('Cotton cultivation guide: Plant in March-April in warm, well-drained soil. Use treated seeds and space rows properly. Harvest when bolls are open and dry, then store cotton in dry, ventilated bales.')
            suggestions.append('Fertilizer Advice: Apply NPK (20-10-10) at 120 kg/ha at planting, with 60 kg/ha nitrogen during vegetative growth. Add zinc and boron if deficient.')
            suggestions.append('Pesticide Advice: For bollworms, use pheromone traps and neem oil; for whiteflies, use acetamiprid (0.2g/liter).')
        elif any_keyword(['potato', 'ఉరుక్కాయ']):
            suggestions.append('Potato cultivation guide: Plant in well-drained, fertile soil with good organic matter. Keep soil evenly moist, especially during tuber formation. Harvest when foliage yellows, dry tubers, and store in cool, dark, ventilated conditions.')
            suggestions.append('Fertilizer Advice: Apply NPK (15-15-30) at 1500 kg/ha at planting, with 50 kg/ha nitrogen at tuber initiation.')
            suggestions.append('Pesticide Advice: For late blight, use mancozeb (2g/liter); for beetles, use neem oil or hand-picking.')
        elif any_keyword(['corn', 'maize', 'జొన్న']):
            suggestions.append('Corn cultivation guide: Plant in warm, fertile soil with good sunlight. Harvest when kernels are hard and dry, and store in well-ventilated bins at 13-15% moisture.')
            suggestions.append('Fertilizer Advice: Apply NPK (30-15-0) at 120 kg/ha at planting, with 60 kg/ha nitrogen at knee-high stage.')
            suggestions.append('Pesticide Advice: For borers, use neem oil or spinosad (0.5 ml/liter); for aphids, use imidacloprid (0.3 ml/liter).')

    if not matched:
        suggestions.append('Provide more details about your crop concern: Is it about harvesting, planting, disease, pests, watering, soil, nutrients, or storage? The more specific you are, the better guidance I can provide.')

    return translate_text(' '.join(suggestions), language)


def get_crop_prices():
    # Read crop prices from CSV so they can be updated easily
    prices = []
    csv_path = os.path.join(os.path.dirname(__file__), 'crop_prices.csv')
    if os.path.isfile(csv_path):
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            # Skip comment lines
            lines = [line for line in csvfile if not line.strip().startswith('#') and line.strip()]
            reader = csv.DictReader(lines, fieldnames=['name', 'price', 'unit', 'market'])
            for row in reader:
                # Skip header row if present
                if row['name'] == 'name':
                    continue
                prices.append({
                    'name': row['name'],
                    'price': row['price'],
                    'unit': row['unit'],
                    'market': row['market']
                })
    return prices


def analyze_plant_image(filepath, language='en'):
    # Mock plant disease analysis
    # In a real implementation, use an API like Plant.id or a ML model
    diagnosis = "The plant appears healthy. No visible diseases detected. Ensure proper watering and nutrition."
    # The following code is disabled to avoid import errors:
    # import numpy as np
    # from PIL import Image
    # import tensorflow as tf
    # from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
    # ...model code disabled...
    return translate_text(diagnosis, language)


def detect_language(text):
    try:
        result = run_async(translator.detect(text))
        return result.lang
    except:
        return None


def translate_text(text, language):
    if language == 'en':
        return text

    try:
        translated = run_async(translator.translate(text, dest=language))
        return translated.text
    except Exception:
        return text



# Dashboard route for analytics and visualizations
@app.route('/dashboard')
def dashboard():
    # Feedback analytics: count by crop and by issue keyword
    feedbacks = load_feedback()
    # Count feedback by crop
    crop_counts = {}
    for fb in feedbacks:
        crop = fb.get('crop', 'Unknown')
        crop_counts[crop] = crop_counts.get(crop, 0) + 1
    # Count feedback by issue keyword
    issue_keywords = ['dry', 'pest', 'disease', 'yield', 'soil', 'weather']
    feedback_data = {k: 0 for k in issue_keywords}
    for fb in feedbacks:
        notes = fb.get('notes', '').lower()
        for k in issue_keywords:
            if k in notes:
                feedback_data[k] += 1
    return render_template('dashboard.html', feedback_data=feedback_data, crop_data=crop_counts)



# Crop price prediction (regression ML)
@app.route('/predict-price', methods=['GET', 'POST'])
def predict_price():
    # Load crop price data
    csv_path = os.path.join(os.path.dirname(__file__), 'crop_prices.csv')
    # Read CSV, skip comment lines, set headers explicitly
    import io
    with open(csv_path, encoding='utf-8') as f:
        lines = [line for line in f if not line.strip().startswith('#') and line.strip()]
    df = pd.read_csv(io.StringIO(''.join(lines)), names=['name', 'price', 'unit', 'market'])
    crops = sorted(df['name'].unique())
    markets = sorted(df['market'].unique())
    predicted_price = None
    selected_crop = None
    selected_market = None
    if request.method == 'POST':
        selected_crop = request.form['crop']
        selected_market = request.form['market']
        # Prepare features: one-hot encode crop and market
        X = pd.get_dummies(df[['name', 'market']])
        y = df['price'].astype(float)
        model = LinearRegression()
        model.fit(X, y)
        # Prepare input for prediction
        input_dict = {col: 0 for col in X.columns}
        crop_col = f"name_{selected_crop}"
        market_col = f"market_{selected_market}"
        if crop_col in input_dict:
            input_dict[crop_col] = 1
        if market_col in input_dict:
            input_dict[market_col] = 1
        input_vec = np.array([input_dict[col] for col in X.columns]).reshape(1, -1)
        predicted_price = round(float(model.predict(input_vec)[0]), 2)
    return render_template('predict_price.html', crops=crops, markets=markets, predicted_price=predicted_price, selected_crop=selected_crop, selected_market=selected_market)

# FAQ/help route
@app.route('/faq')
def faq():
    return render_template('faq.html')

if __name__ == '__main__':
    app.run(debug=True)