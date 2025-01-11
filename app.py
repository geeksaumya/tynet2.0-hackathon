from flask import Flask, render_template, request, redirect, url_for, session
import requests
import pywhatkit

app = Flask(__name__)
app.secret_key = 'sos_app'

POLICE_CONTACT = "+917506777100"


def get_live_location():
    try:
        ip_response = requests.get("https://ipinfo.io/json")
        location_data = ip_response.json()
        location = location_data.get("loc").split(',')
        latitude, longitude = float(location[0]), float(location[1])
        return latitude, longitude
    except Exception as e:
        print(f"Error fetching location: {e}")
        return None, None

@app.route('/')
def index():
    emergency_contact = session.get('emergency_contact', '')
    name = session.get('name', '')
    return render_template('index.html', emergency_contact=emergency_contact, name=name)

@app.route('/send_sos', methods=['POST'])
def send_sos():
    name = request.form['name']
    emergency_contact = request.form.get('emergency_contact')

    session['name'] = name
    if emergency_contact:
        session['emergency_contact'] = emergency_contact

    latitude, longitude = get_live_location()
    if latitude is None or longitude is None:
        return "Error fetching location. Please try again later.", 500

    sos_message = f"SOS! {name} is in danger. Live location: https://www.google.com/maps?q={latitude},{longitude}"

    try:
        pywhatkit.sendwhatmsg_instantly(f"+{POLICE_CONTACT}", sos_message)
    except Exception as e:
        print(f"Error sending WhatsApp message to police: {e}")
        return "Error sending SOS message to police. Please check WhatsApp Web and try again.", 500

    if emergency_contact:
        try:
            pywhatkit.sendwhatmsg_instantly(f"+{emergency_contact}", sos_message)
        except Exception as e:
            print(f"Error sending WhatsApp message to emergency contact: {e}")
            return "Error sending SOS message to emergency contact. Please check WhatsApp Web and try again.", 500

    return redirect(url_for('index'))

@app.route('/edit_contact', methods=['GET', 'POST'])
def edit_contact():
    if request.method == 'POST':
        emergency_contact = request.form['emergency_contact']
        session['emergency_contact'] = emergency_contact
        return redirect(url_for('index'))
    emergency_contact = session.get('emergency_contact', '')
    return render_template('edit_contact.html', emergency_contact=emergency_contact)

@app.route('/edit_name', methods=['GET', 'POST'])
def edit_name():
    if request.method == 'POST':
        name = request.form['name']
        session['name'] = name
        return redirect(url_for('index'))
    name = session.get('name', '')
    return render_template('edit_name.html', name=name)

if __name__ == "__main__":
    app.run(debug=True)

