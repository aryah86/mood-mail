#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  5 13:21:19 2026

@author: 245304048
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  5 13:21:19 2026

@author: 245304048
"""

from flask import Flask, render_template, request, redirect, url_for, session
import json, random

app = Flask(__name__)
app.secret_key = 'moodmail-arya-2026-secret'

def load_messages():
    try:
        with open("messages.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"happy": [], "sad": [], "angry": [], "bored": []}

def save_messages(data):
    with open("messages.json", "w") as f:
        json.dump(data, f, indent=2)

def get_mail_allowance():
    """Get remaining mail allowance for user"""
    if 'mail_allowance' not in session:
        session['mail_allowance'] = 1  # First time users get 1 free mail
        session['is_new_user'] = True
    return session['mail_allowance']

def use_mail():
    """Use one mail from allowance"""
    if session.get('mail_allowance', 0) > 0:
        session['mail_allowance'] -= 1
        return True
    return False

def add_mails(count=3):
    """Add mails to allowance after writing"""
    session['mail_allowance'] = session.get('mail_allowance', 0) + count

@app.route("/")
def index():
    # Initialize session on first visit
    get_mail_allowance()
    return render_template("index.html")

@app.route("/emotion", methods=["POST"])
def emotion():
    emotion = request.form["emotion"]
    data = load_messages()
    messages = data.get(emotion, [])
    
    allowance = get_mail_allowance()
    
    # If no allowance, redirect to write page
    if allowance <= 0:
        return redirect(url_for('write', locked='true'))
    
    if not messages:
        messages = [{"text": "No messages yet. Be the first to write one!"}]
    
    # Shuffle messages for random delivery
    messages_copy = messages.copy()
    random.shuffle(messages_copy)
    
    # Store shuffled messages in session for opening
    session['shuffled_messages'] = messages_copy
    session['current_emotion'] = emotion
    
    # Show ALL envelopes (not limited by allowance)
    return render_template("emotion.html", 
                         messages=messages_copy, 
                         emotion=emotion,
                         allowance=allowance)

@app.route("/open/<int:index>", methods=["POST"])
def open_envelope(index):
    emotion = session.get('current_emotion', 'happy')
    shuffled_messages = session.get('shuffled_messages', [])
    
    # Check if user has allowance
    if not use_mail():
        return redirect(url_for('write', locked='true'))
    
    # Get the message from shuffled list
    if index < len(shuffled_messages):
        message_text = shuffled_messages[index]["text"]
    else:
        message_text = "This envelope is empty. Try another one!"
    
    return render_template("message.html", 
                         message=message_text,
                         emotion=emotion)

@app.route("/write")
def write():
    locked = request.args.get('locked', False)
    allowance = get_mail_allowance()
    return render_template("write.html", locked=locked, allowance=allowance)

@app.route("/submit", methods=["POST"])
def submit():
    mood = request.form["mood"]
    message = request.form["message"]
    
    data = load_messages()
    
    if mood not in data:
        data[mood] = []
    
    data[mood].append({"text": message})
    save_messages(data)
    
    # Unlock 3 mails for the user
    add_mails(3)
    
    return render_template("thankyou.html", unlocked=3)

if __name__ == "__main__":
    app.run(debug=True)

    

