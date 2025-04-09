from flask import Flask, render_template, request,make_response,flash,url_for,redirect
import googletrans
from googletrans import Translator
import gtts
from gtts import gTTS
import time
import sqlite3
from IPython.display import Audio
import os
app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024



ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov'} 

language_codes = googletrans.LANGUAGES
languages = [{"code": code, "name": name} for code, name in language_codes.items()]






def translate_text(text, target_lang):
    translator = Translator()
    translation = translator.translate(text, dest=target_lang)
    return translation.text

@app.route("/", methods=["GET", "POST"])
def translate():
    if request.method == "POST":
        input_text = request.form.get("input_text")
        input_text = input_text.lower()
        print(input_text)

        with sqlite3.connect('medico.db') as db:
            c = db.cursor()
        find_details = ('SELECT * FROM medicine WHERE Name = ?')
        c.execute(find_details,[input_text.lower()])
        result = c.fetchall()
        data=result[0][1]
        text='Medicine Name:{}'.format(input_text)
        for i in data.split('\r\n'):
            text=text+os.linesep+i
        
        target_language = request.form.get("target_language")
        translated_text = translate_text(text, target_language)
        print(translated_text)
        timestamp = int(time.time())
        filename = f"static/op_{timestamp}.mp3"  
        tts = gTTS(translated_text, lang=target_language,slow = False)
        tts.save(filename)  
        return render_template("index.html", languages=languages, input_text=text, translated_text=translated_text, audio_filename=filename)
    return render_template("index.html", languages=languages)


@app.route('/video')
def upload_form():
    # Get the list of available videos in the UPLOAD_FOLDER
    videos = [video for video in os.listdir(app.config['UPLOAD_FOLDER']) if video.endswith(tuple(ALLOWED_EXTENSIONS))]
    return render_template('upload.html', videos=videos)

@app.route('/video', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No video selected for uploading')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Video successfully uploaded and displayed below')
        return render_template('upload.html', filename=filename)

    flash('Invalid file format. Allowed formats are: mp4, avi, mkv, mov')
    return redirect(request.url)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/display/<filename>')
def display_video(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == "__main__":
    app.run(debug=True)
