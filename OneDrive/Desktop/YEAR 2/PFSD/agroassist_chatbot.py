from flask import Blueprint, render_template, request, session, redirect, url_for

agroassist_bp = Blueprint('agroassist', __name__)

# Simple AgroAssist response logic

def get_agroassist_response(user_input, get_crop_prices):
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

@agroassist_bp.route('/agroassist', methods=['GET', 'POST'])
def agroassist():
    from app import get_crop_prices  # Import here to avoid circular import
    if 'chatlog' not in session:
        session['chatlog'] = []
    chatlog = session['chatlog']
    if request.method == 'POST':
        user_input = request.form['user_input']
        chatlog.append({'role': 'user', 'text': user_input})
        response = get_agroassist_response(user_input, get_crop_prices)
        chatlog.append({'role': 'bot', 'text': response})
        session['chatlog'] = chatlog
        return redirect(url_for('agroassist.agroassist'))
    return render_template('agroassist.html', chatlog=chatlog)
